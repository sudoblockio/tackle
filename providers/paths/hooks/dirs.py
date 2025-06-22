import os
import pathlib
import tempfile

from tackle import BaseHook, Field


class MakeDirectoryHook(BaseHook):
    """Hook creating a directory."""

    hook_name = 'mkdir'
    path: str = Field(..., description="The path to file or directory")

    args: list = ['path']
    _docs_order = 1

    def exec(self) -> str:
        pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)
        return self.path


class MakeTempDirectoryHook(BaseHook):
    """Hook creating a temporary directory."""

    hook_name = 'temp_dir'
    _docs_order = 2

    def exec(self) -> str:
        return tempfile.mkdtemp()


class ChangeDirectoryHook(BaseHook):
    """Hook changing directory."""

    hook_name = 'chdir'
    path: str
    args: list = ['path']

    def exec(self):
        os.chdir(self.path)
