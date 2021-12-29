"""List directory hook."""
from typing import Union, List
import os
import logging

from tackle.models import BaseHook, Field

logger = logging.getLogger(__name__)


class ListdirHook(BaseHook):
    """
    Hook  for `listdir`. Lists the contents of a directory.

    :return: A list of contents of the `path` if input is string,
        A map with keys of items if input `path` is list.
    """

    hook_type: str = 'listdir'
    ignore_hidden_files: bool = Field(
        None, description="Boolean to ignore hidden files"
    )
    path: Union[List[str], str] = Field(
        None, description="String or list to directories to list"
    )
    sort: bool = Field(False, description="Boolean to sort the output")

    _args: list = ['path']

    def execute(self):
        if isinstance(self.path, str):
            files = os.listdir(os.path.expanduser(self.path))
            if self.sort:
                files.sort()
            if self.ignore_hidden_files:
                return [f for f in files if not f.startswith('.')]
            else:
                return files

        if isinstance(self.path, list):
            contents = {}
            for i in self.path:
                contents[i] = os.listdir(os.path.expanduser(i))
                if self.sort:
                    contents[i].sort()
            return contents
