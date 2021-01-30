# -*- coding: utf-8 -*-

"""Symlink hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import os
import logging
from typing import Any

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class SymlinkHook(BaseHook):
    """
    Hook creating symlinks wrapping `os.symlink` functionality.

    :param src: String or list of sources, either a directories or files
    :param dst: String for path to copy to
    :param target_is_directory: The default value of this parameter is False. If
        the specified target path is directory then its value should be True.
    :param dir_fd: A file descriptor referring to a directory.
    :return: None
    """

    type: str = 'symlink'
    src: str
    dst: str
    target_is_directory: bool = False
    overwrite: bool = False

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.src = os.path.abspath(os.path.expanduser(os.path.expandvars(self.src)))
        self.dst = os.path.abspath(os.path.expanduser(os.path.expandvars(self.dst)))

    def execute(self) -> None:
        """Run the hook."""
        if self.overwrite and os.path.islink(self.dst):
            os.symlink(self.src, ''.join([self.dst, '.tmp']),
                       target_is_directory=self.target_is_directory)
            os.rename(self.dst + '.tmp', self.dst)
        elif self.overwrite and os.path.isfile(self.dst):
            os.remove(self.dst)
            os.symlink(src=self.src, dst=self.dst,
                       target_is_directory=self.target_is_directory)
        else:
            os.symlink(src=self.src, dst=self.dst,
                       target_is_directory=self.target_is_directory)
