# -*- coding: utf-8 -*-

import os
import json
import shutil
import tempfile

from pygit2 import (
    Repository,
    discover_repository,
    GIT_MERGE_ANALYSIS_UP_TO_DATE,
    GIT_MERGE_ANALYSIS_FASTFORWARD,
    GIT_MERGE_ANALYSIS_NORMAL
)
from cookiecutter.main import cookiecutter

__worktree_name__ = 'templating'
__template_branch__ = 'template'
__notes_template_ref__ = 'refs/notes/template'
__notes_context_ref__ = 'refs/notes/context'
__commit_apply_message__ = 'Apply template'
__commit_merge_message__ = 'Installed template'

class TemporaryWorktree():
    def __init__(self, upstream, name):
        if name in upstream.list_worktrees():
            raise Exception('Worktree %s already exists' % __worktree_name__)

        self.upstream = upstream
        self.name = name
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, name)
        self.obj = None
        self.repo = None

    def __enter__(self):
        self.obj = self.upstream.add_worktree(self.name, self.path)
        self.repo = Repository(self.obj.path)
        return self

    def __exit__(self, type, value, traceback):
        # Remove temp directory
        shutil.rmtree(self.tmp)

        # Prune temp worktree
        if self.obj is not None:
            self.obj.prune(True)

        # Remove worktree ref in upstream repository
        try:
            self.upstream.lookup_branch(self.name).delete()
        except:
            pass

class Milhoja(object):
    def __init__(self, repo):
        self.repo = repo

    def install(self, template, checkout='master', extra_context=None, no_input=False):
        if extra_context is None:
            extra_context = {}

        # Assert template branch doesn't exist or raise conflict
        if __template_branch__ in self.repo.listall_branches():
            raise Exception('Branch %s already exists' % __template_branch__)

        if __worktree_name__ in self.repo.list_worktrees():
            raise Exception('Worktree %s already exists' % __worktree_name__)

        # Create temporary worktree
        with TemporaryWorktree(self.repo, __worktree_name__) as worktree:
            # Apply cookiecutter
            # NOTE: cookiecutter has been patched to return generated context
            _, context = cookiecutter(
                template, checkout, no_input,
                extra_context=extra_context,
                replay=False,
                overwrite_if_exists=True,
                output_dir=worktree.path,
                strip=True
            )

            # Stage changes
            worktree.repo.index.add_all()
            worktree.repo.index.write()
            tree = worktree.repo.index.write_tree()

            # Create an orphaned commit
            oid = worktree.repo.create_commit(
                None,
                worktree.repo.default_signature, worktree.repo.default_signature,
                __commit_apply_message__,
                tree,
                []
            )

            # Create a branch which target orphaned commit
            branch = self.repo.create_branch(__template_branch__, self.repo.get(oid))

            # Optionally, set worktree HEAD to this branch (useful for debugging)
            # Optional ? Obviously the tmp worktree will be removed in __exit__
            worktree.repo.set_head(branch.name)

        # Create a object where we store template information
        info = dict(
            src=template,
            ref=checkout
        )

        # Create Git Note with serialized template references
        self.repo.create_note(
            json.dumps(info),
            self.repo.default_signature,
            self.repo.default_signature,
            oid.__str__(),
            __notes_template_ref__
        )
        # Create Git Note with serialized context
        self.repo.create_note(
            json.dumps(context),
            self.repo.default_signature,
            self.repo.default_signature,
            oid.__str__(),
            __notes_context_ref__
        )

        # Analyze merge between template branch and HEAD
        analysis, _ = self.repo.merge_analysis(branch.target)

        # Up to date, nothing to do
        if analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE:
            # Should append if user reinstalled an existing template
            # TODO log this info to user
            pass

        elif analysis & GIT_MERGE_ANALYSIS_FASTFORWARD or analysis & GIT_MERGE_ANALYSIS_NORMAL:
            # Let's merge template changes.
            index = self.repo.merge_commits(self.repo.head.target, branch.target)

            # TODO What to do with conflict ?
            #        -> Let user resolve ?
            #        -> Raise an error after analysis ?
            assert index.conflicts is None

            # Write index
            tree = index.write_tree(self.repo)

            # Commit it
            self.repo.create_commit(
                'HEAD',
                self.repo.default_signature,
                self.repo.default_signature,
                __commit_merge_message__,
                tree,
                [self.repo.head.target, branch.target]
            )

            self.repo.checkout('HEAD')
        else:
            raise AssertionError('Unknown merge analysis result')


    def upgrade(self, checkout='master', extra_context=None, no_input=False):
        if extra_context is None:
            extra_context = {}

        # TODO Assert template branch exist or raise an error

        # TODO Find first template commit in template branch (root).
        # TODO Try to fetch note from 'milhoja/template' namespace

        # TODO Get last commit in 'template'
        # TODO Try to fetch note from 'milhoja/context' namespace
        # TODO Parse context from this note: old_context

        # TODO Merge old_context and extra_context (priority to extra_context)

        # TODO Create temporary EMPTY worktree

        # TODO Move HEAD to template branch WITHOUT checkout

        # TODO Apply cookiecutter with merged context
        # TODO Such in installation, cookiecutter MUST return a tuple with
        #      context used

        # TODO Commit changes

        # TODO Create Git Note in 'milhoja/context' namespace with context from cc

        # TODO Attach this notes to last commit

        # TODO Remove worktree (unlink + prune)

        # TODO In self.path: merge template branch into HEAD
        # NOTE Which kind of merge to do ?

        # TODO Such as installation: what to do with conflict ?
        #        -> Let user resolve ?
        #        -> Raise an error after analysis ?
        pass
