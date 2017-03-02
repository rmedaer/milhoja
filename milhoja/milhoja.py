# -*- coding: utf-8 -*-


class Milhoja(object):
    def __init__(self, path, template_branch='template'):
        self.path = path
        self.template_branch = template_branch
        pass

    def install(self, template, checkout='master', extra_context=None, no_input=False):
        if extra_context is None:
            extra_context = {}

        # TODO Assert template branch doesn't exist or raise conflict

        # TODO Create temporary worktree

        # TODO Create orphaned branch 'template' (self.template_branch)

        # TODO Apply cookiecutter
        # TODO we need to get back cookiecutter context, it needs to patch
        #      cookiecutter to return created context (a tuple) !
        #_, context = cookiecutter(
        #     template, checkout, no_input,
        #     extra_context=extra_context,
        #     replay=replay,
        #     overwrite_if_exists=True,
        #     output_dir=worktree,
        #     strip=True
        # )

        # TODO Commit changes

        # TODO Create Git Note in 'milhoja/template' namespace with template references

        # TODO Create Git Note in 'milhoja/context' namespace with context

        # TODO Attach this notes to last commit

        # TODO Remove worktree (unlink + prune)

        # TODO In self.path: merge template branch into HEAD

        # TODO What to do with conflict ?
        #        -> Let user resolve ?
        #        -> Raise an error after analysis ?

        pass

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
