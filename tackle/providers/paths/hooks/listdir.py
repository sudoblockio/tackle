import os

from tackle.models import BaseHook, Field


class ListdirHook(BaseHook):
    """Hook for `listdir`. Lists the contents of a directory."""

    hook_type: str = 'listdir'
    path: str = Field('.', description="Path to directory to list contents.")
    sort: bool = Field(False, description="Boolean to sort the output")
    ignore_hidden_files: bool = Field(
        None, description="Boolean to ignore hidden files"
    )

    args: list = ['path']
    _docs_order = 2

    def exec(self) -> list:
        files = os.listdir(os.path.expanduser(self.path))
        if self.sort:
            files.sort()
        if self.ignore_hidden_files:
            return [f for f in files if not f.startswith('.')]
        else:
            return files
