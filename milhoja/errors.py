# -*- coding: utf-8 -*-

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
        """
        Initializing the exception with small message.
        """
        super(TemplateConflictException, self).__init__('Template already installed')

class WorktreeException(MilhojaException):
    """
    Error raised when worktree could not be initialized.
    """

    def __init__(self, worktree_name, worktree_path):
        super(WorktreeException, self).__init__(
            'Worktree \'%s\' could not be initialized in path \'%s\'' % (worktree_name, worktree_path)
        )

class WorktreeConflictException(MilhojaException):
    """
    Error raised when worktree already exist.
    """

    def __init__(self, worktree_name=None):
        """
        Initialized the exception based on worktree name.
        """
        if worktree_name:
            super(WorktreeConflictException, self).__init__('Worktree %s already exists' % worktree_name)
        else:
            super(WorktreeConflictException, self).__init__('Worktree already exists')

class TemplateNotFoundException(MilhojaException):
    """
    Error raised when template could not be found.
    """

    def __init__(self):
        """
        Initializing the exception with small message.
        """
        super(TemplateNotFoundException, self).__init__('Template could not be found')

class RepositoryNotFoundException(MilhojaException):
    """
    Error raised when Git repository could not be found.
    """

    def __init__(self):
        """
        Initializing the exception with small message.
        """
        super(RepositoryNotFoundException, self).__init__('Could not find Git repository')

class RepositoryInitializationException(MilhojaException):
    """
    Error raised when Git repository could not be initialized.
    """

    def __init__(self):
        """
        Initializing the exception with small message.
        """
        super(RepositoryInitializationException, self).__init__('Failed to initialize Git repository')

class RepositoryEmptyException(MilhojaException):
    """
    Error raised when Git repository is unborn.
    """

    def __init__(self):
        """
        Initializing the exception with small message.
        """
        super(RepositoryEmptyException, self).__init__('Target repository is empty')
