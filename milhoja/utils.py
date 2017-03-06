# -*- coding: utf-8 -*-

from pygit2 import (
    Repository,
    discover_repository,
    init_repository
)

__commit_init_message__ = 'Initialized repository'

def open_repository(path):
    try:
        return Repository(discover_repository(path))
    except:
        raise Exception('Failed to open Git repository')

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
        raise Exception('Failed to initialize Git repository')
