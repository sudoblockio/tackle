import pathlib
import tempfile

from tackle.models import BaseHook, Field


class MakeDirectoryHook(BaseHook):
    """Hook creating a directory."""

    hook_type: str = 'mkdir'
    path: str = Field(..., description="The path to file or directory")

    args: list = ['path']
    _docs_order = 1

    def exec(self) -> str:
        pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)
        return self.path


class MakeTempDirectoryHook(BaseHook):
    """Hook creating a temporary directory."""

    hook_type: str = 'temp_dir'
    _docs_order = 2

    def exec(self) -> str:
        return tempfile.mkdtemp()
