# -*- coding: utf-8 -*-

from pygit2 import (
    Repository,
    discover_repository,
    init_repository
)

__commit_init_message__ = 'Initialized repository'

def open_or_init_repository(path):
    # Try to open the repository
    try:
        repo = Repository(discover_repository(path))
    except KeyError:
        repo = init_repository(path)
        init_commit = repo.create_commit(
            'HEAD',
            repo.default_signature, repo.default_signature,
            __commit_init_message__,
            repo.index.write_tree(),
            []
        )

    return repo
