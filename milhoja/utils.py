# -*- coding: utf-8 -*-

from pygit2 import (
    Repository,
    discover_repository,
    init_repository
)
from .errors import (
    RepositoryNotFoundException,
    RepositoryInitializationException
)

__commit_init_message__ = 'Initialized repository'

def open_repository(path):
    try:
        return Repository(discover_repository(path))
    except:
        raise RepositoryNotFoundException()

def open_or_init_repository(path):
    try:
        return open_repository(path)
    except:
        pass

    try:
        repo = init_repository(path)
        repo.create_commit(
            'HEAD',
            repo.default_signature, repo.default_signature,
            __commit_init_message__,
            repo.index.write_tree(),
            []
        )
        return repo
    except:
        raise RepositoryInitializationException()
