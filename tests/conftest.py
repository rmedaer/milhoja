import os
import tempfile
import stat
import shutil
from types import TracebackType
from typing import Optional, Type
import pytest
from pygit2 import Repository


def force_rm_handle(remove_path, path, excinfo):
    os.chmod(
        path,
        os.stat(path).st_mode | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
    )
    remove_path(path)


class TemporaryRepository:
    """Taken from pygit2 tests: https://github.com/libgit2/pygit2/blob/master/test/utils.py"""

    def __enter__(self) -> 'TemporaryRepository':
        name = 'testrepo.git'
        repo_path = os.path.join(os.path.dirname(__file__), name)
        self.temp_dir = tempfile.mkdtemp()
        temp_repo_path = os.path.join(self.temp_dir, name)
        shutil.copytree(repo_path, temp_repo_path)
        return temp_repo_path

    def __exit__(self, type: Optional[Type[BaseException]], value: Optional[BaseException],
                 traceback: TracebackType):
        if os.path.exists(self.temp_dir):
            onerror = lambda func, path, e: force_rm_handle(func, self.temp_dir, e)
            shutil.rmtree(self.temp_dir, onerror=onerror)


@pytest.fixture
def repo() -> Repository:
    with TemporaryRepository() as repo_path:
        yield Repository(repo_path)
