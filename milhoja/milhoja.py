# -*- coding: utf-8 -*-

import os
import six
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
from .errors import (
    TemplateConflictException,
    WorktreeConflictException,
    WorktreeException,
    TemplateNotFoundException,
    RepositoryEmptyException
)

__worktree_name__ = 'templating'
__template_branch__ = 'template'
__notes_template_ref__ = 'refs/notes/template'
__notes_context_ref__ = 'refs/notes/context'
__commit_prepare_install_message__ = 'Prepared template installation'
__commit_install_message__ = 'Installed template \'%s\''
__commit_prepare_upgrade_message__ = 'Prepared template upgrade'
__commit_upgrade_message__ = 'Upgraded template \'%s\''
__key_source__ = 'src'
__key_reference__ = 'ref'
__key_context__ = 'ctx'

class TemporaryWorktree():
    def __init__(self, upstream, name, empty=False, prune=True):
        if name in upstream.list_worktrees():
            raise WorktreeConflictException(name)

        self.upstream = upstream
        self.name = name
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, name)
        self.obj = None
        self.repo = None
        self.empty = empty
        self.prune = prune

    def __enter__(self):
        if self.upstream.head_is_unborn:
            raise RepositoryEmptyException()

        try:
            self.obj = self.upstream.add_worktree(self.name, self.path)
        except ValueError:
            raise WorktreeException(self.name, self.path)

        self.repo = Repository(self.obj.path)

        # If the worktree needs cleanup
        if self.empty:
            for entry in self.repo[self.repo.head.target].tree:
                if os.path.isdir(os.path.join(self.path, entry.name)):
                    shutil.rmtree(os.path.join(self.path, entry.name))
                else:
                    os.remove(os.path.join(self.path, entry.name))

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
            raise TemplateNotFoundException()

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

        info = json.loads(note.message)
        assert isinstance(info[__key_source__], six.string_types)
        assert isinstance(info[__key_reference__], six.string_types)

        return info[__key_source__], info[__key_reference__]

    def get_context(self):
        commit = self.get_last_commit()
        note = self.repo.lookup_note(commit.id.__str__(), __notes_template_ref__)

        info = json.loads(note.message)
        assert isinstance(info[__key_context__], dict)

        return info[__key_context__]

    def create_note(self, commit, source, reference, context):
        # Create Git Note with serialized template references and context
        self.repo.create_note(
            json.dumps({
                __key_source__: source,
                __key_reference__: reference,
                __key_context__: context
            }),
            self.repo.default_signature,
            self.repo.default_signature,
            commit.hex,
            __notes_template_ref__
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
            self.repo.merge(branch.target)

            # TODO What to do with conflict ?
            #        -> Let user resolve ?
            #        -> Raise an error after analysis ?
            assert self.repo.index.conflicts is None

            # Write index
            tree = self.repo.index.write_tree()

            # Commit it
            self.repo.create_commit(
                'HEAD',
                self.repo.default_signature,
                self.repo.default_signature,
                message,
                tree,
                [self.repo.head.target, branch.target]
            )

            # Clean up repository state
            self.repo.state_cleanup()

            self.repo.checkout('HEAD')
        else:
            raise AssertionError('Unknown merge analysis result')

    def install(self, template, checkout='master', extra_context=None, no_input=False):
        if extra_context is None:
            extra_context = {}

        # Assert template branch doesn't exist or raise conflict
        if self.is_installed():
            raise TemplateConflictException()

        # Create temporary worktree
        with TemporaryWorktree(self.repo, __worktree_name__, empty=True) as worktree:
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

        # Create notes with meta data (template + context)
        self.create_note(commit, template, checkout, context)

        # Let's merge our changes into HEAD
        self.merge_template_branch(__commit_install_message__ % template)


    def upgrade(self, checkout='master', extra_context=None, no_input=False):
        if extra_context is None:
            extra_context = {}

        # Assert template branch exist or raise an error
        if not self.is_installed():
            raise TemplateNotFoundException()

        # Fetch template information
        template, _ = self.get_template()

        # Get last context used to apply template
        context = self.get_context()

        # Merge original context and extra_context (priority to extra_context)
        context.update(extra_context)

        # Create temporary EMPTY worktree
        with TemporaryWorktree(self.repo, __worktree_name__, empty=True) as worktree:
            # Set HEAD to template branch
            branch = worktree.repo.lookup_branch(__template_branch__)
            worktree.repo.set_head(branch.name)

            # Apply cookiecutter with merged context
            # NOTE: cookiecutter has been patched to return generated context
            _, context = cookiecutter(
                template, checkout, no_input,
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

        # Create notes with meta data (template + context)
        self.create_note(commit, template, checkout, context)

        # Let's merge our changes into HEAD
        self.merge_template_branch(__commit_upgrade_message__ % template)
