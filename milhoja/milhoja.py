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
    GIT_MERGE_ANALYSIS_NORMAL,
    GIT_SORT_TOPOLOGICAL,
    GIT_SORT_REVERSE
)
from cookiecutter.main import cookiecutter

__worktree_name__ = 'templating'
__template_branch__ = 'template'
__notes_template_ref__ = 'refs/notes/template'
__notes_context_ref__ = 'refs/notes/context'
__commit_prepare_install_message__ = 'Prepared template installation'
__commit_install_message__ = 'Installed template \'%s\''
__commit_prepare_upgrade_message__ = 'Prepared template upgrade'
__commit_upgrade_message__ = 'Upgraded template \'%s\''

class TemporaryWorktree():
    def __init__(self, upstream, name, prune=True):
        if name in upstream.list_worktrees():
            raise Exception('Worktree %s already exists' % name)

        self.upstream = upstream
        self.name = name
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, name)
        self.obj = None
        self.repo = None
        self.prune = prune

    def __enter__(self):
        self.obj = self.upstream.add_worktree(self.name, self.path)
        self.repo = Repository(self.obj.path)
        return self

    def __exit__(self, type, value, traceback):
        # Skip auto prune if flag is enable
        if not self.prune:
            return

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

    def is_installed(self):
        return __template_branch__ in self.repo.listall_branches()

    def get_template_branch(self):
        branch = self.repo.lookup_branch(__template_branch__)

        if branch is None:
            raise Exception('Template branch not found')

        return branch

    def get_root_commit(self):
        return self.repo.walk(
            self.get_template_branch().target,
            GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE
        ).next()

    def get_last_commit(self):
        return self.repo.get(self.get_template_branch().target)

    def get_template(self):
        commit = self.get_last_commit()
        note = self.repo.lookup_note(commit.id.__str__(), __notes_template_ref__)
        return json.loads(note.message)

    def get_context(self):
        # An alias of "get_last_context"
        return self.get_last_context()

    def get_last_context(self):
        commit = self.get_last_commit()
        note = self.repo.lookup_note(commit.id.__str__(), __notes_context_ref__)

        context = json.loads(note.message)
        assert isinstance(context, dict)

        return context

    def create_notes(self, commit, info, context):
        # Create Git Note with serialized template references
        self.repo.create_note(
            json.dumps(info),
            self.repo.default_signature,
            self.repo.default_signature,
            commit.hex,
            __notes_template_ref__
        )
        # Create Git Note with serialized context
        self.repo.create_note(
            json.dumps(context),
            self.repo.default_signature,
            self.repo.default_signature,
            commit.hex,
            __notes_context_ref__
        )

    def merge_template_branch(self, message):
        # Lookup template branch
        branch = self.repo.lookup_branch(__template_branch__)

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
                message,
                tree,
                [self.repo.head.target, branch.target]
            )

            self.repo.checkout('HEAD')
        else:
            raise AssertionError('Unknown merge analysis result')

    def install(self, template, checkout='master', extra_context=None, no_input=False):
        if extra_context is None:
            extra_context = {}

        # Assert template branch doesn't exist or raise conflict
        if self.is_installed():
            raise Exception('Template already installed')

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
                __commit_prepare_install_message__,
                tree,
                []
            )
            commit = self.repo.get(oid)

            # Create a branch which target orphaned commit
            branch = self.repo.create_branch(__template_branch__, commit)

            # Optionally, set worktree HEAD to this branch (useful for debugging)
            # Optional ? Obviously the tmp worktree will be removed in __exit__
            worktree.repo.set_head(branch.name)

        # Create a object where we store template information
        info = dict(
            src=template,
            ref=checkout
        )

        # Create notes with meta data (template + context)
        self.create_notes(commit, info, context)

        # Let's merge our changes into HEAD
        self.merge_template_branch(__commit_install_message__ % template)


    def upgrade(self, checkout='master', extra_context=None, no_input=False):
        if extra_context is None:
            extra_context = {}

        # Assert template branch exist or raise an error
        if not self.is_installed():
            raise Exception('Not any template installed')

        # Fetch template information
        info = self.get_template()

        # Get last context used to apply template
        context = self.get_last_context()

        # Merge original context and extra_context (priority to extra_context)
        context.update(extra_context)

        # Create temporary EMPTY worktree
        with TemporaryWorktree(self.repo, __worktree_name__) as worktree:
            # Set HEAD to template branch
            branch = worktree.repo.lookup_branch(__template_branch__)
            worktree.repo.set_head(branch.name)

            # Apply cookiecutter with merged context
            # NOTE: cookiecutter has been patched to return generated context
            _, context = cookiecutter(
                info['src'], checkout, no_input,
                extra_context=context,
                replay=False,
                overwrite_if_exists=True,
                output_dir=worktree.path,
                strip=True
            )

            # Stage changes
            worktree.repo.index.read()
            worktree.repo.index.add_all()
            worktree.repo.index.write()
            tree = worktree.repo.index.write_tree()

            # Create commit on
            oid = worktree.repo.create_commit(
                'HEAD',
                worktree.repo.default_signature, worktree.repo.default_signature,
                __commit_prepare_upgrade_message__,
                tree,
                [worktree.repo.head.target]
            )
            commit = worktree.repo.get(oid)

        # Make template branch ref to created commit
        self.repo.lookup_branch(__template_branch__).set_target(commit.hex)

        # Create a object where we store template information
        info = dict(
            src=info['src'],
            ref=checkout
        )

        # Create notes with meta data (template + context)
        self.create_notes(commit, info, context)

        # Let's merge our changes into HEAD
        self.merge_template_branch(__commit_upgrade_message__ % info['src'])
