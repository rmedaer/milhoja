class MilhojaException(Exception):
    """
    Abstract Milhoja generic exception.
    """
    pass


class TemplateConflictException(MilhojaException):
    """
    Error raised when a template is already installed.
    """

    def __init__(self):
        super().__init__('Template already installed')


class WorktreeException(MilhojaException):
    """
    Error raised when worktree could not be initialized.
    """

    def __init__(self, worktree_name, worktree_path):
        super().__init__(
            f'Worktree \'{worktree_name}\' could not be initialized in path \'{worktree_path}\''
        )


class WorktreeConflictException(MilhojaException):
    """
    Error raised when worktree already exist.
    """

    def __init__(self, worktree_name=None):
        if worktree_name:
            super().__init__(f'Worktree {worktree_name} already exists')
        else:
            super().__init__('Worktree already exists')


class TemplateNotFoundException(MilhojaException):
    """
    Error raised when template could not be found.
    """

    def __init__(self):
        super().__init__('Template could not be found')


class RepositoryEmptyException(MilhojaException):
    """
    Error raised when Git repository is unborn.
    """

    def __init__(self):
        super().__init__('Target repository is empty')


class MergeConflictException(MilhojaException):
    """
    Error raised when we cannot merge the template commit with the target branch.
    """
    pass
