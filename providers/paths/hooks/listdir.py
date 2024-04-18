import os
import re
from typing import Union

from tackle import BaseHook, Field


class ListdirHook(BaseHook):
    """Hook for `listdir`. Lists the contents of a directory."""

    hook_name = 'listdir'
    path: str = Field('.', description="Path to directory to list contents.")
    sort: bool = Field(False, description="Boolean to sort the output")
    ignore_hidden: bool = Field(
        False, description="Boolean to ignore hidden files or directories"
    )
    ignore_hidden_files: bool = Field(
        False, description="Boolean to ignore hidden files"
    )
    ignore_hidden_directories: bool = Field(
        False, description="Boolean to ignore hidden directories"
    )
    only_files: bool = Field(False, description="Only return files.")
    only_directories: bool = Field(False, description="Only return directories.")

    exclude: Union[str, list] = Field(
        None, description="A list or string of regexes to ignore."
    )

    args: list = ['path']
    _docs_order = 2

    def exec(self) -> list:
        files = os.listdir(os.path.expanduser(os.path.expandvars(self.path)))
        if self.sort:
            files.sort()
        if self.ignore_hidden:
            files = [f for f in files if not f.startswith('.')]
        if self.ignore_hidden_files:
            files = [
                f
                for f in files
                if not (
                    f.startswith('.') and os.path.isfile(os.path.join(self.path, f))
                )
            ]
        if self.ignore_hidden_directories:
            files = [
                f
                for f in files
                if not (f.startswith('.') and os.path.isdir(os.path.join(self.path, f)))
            ]
        if self.only_files:
            files = [f for f in files if os.path.isfile(os.path.join(self.path, f))]
        if self.only_directories:
            files = [f for f in files if os.path.isdir(os.path.join(self.path, f))]

        if self.exclude is not None:
            if isinstance(self.exclude, str):
                self.exclude = [self.exclude]
            for e in self.exclude:
                files = [f for f in files if not re.match(e, f)]

        return files
