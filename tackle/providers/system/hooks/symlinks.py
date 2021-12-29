"""Symlink hooks."""
import os
import logging
from typing import Any

from tackle.models import BaseHook, Field

logger = logging.getLogger(__name__)


class SymlinkHook(BaseHook):
    """Hook creating symlinks wrapping `os.symlink` functionality."""

    hook_type: str = 'symlink'
    src: str = Field(
        ..., description="String or list of sources, either a directories or files"
    )
    dst: str = Field(..., description="String for path to copy to")
    target_is_directory: bool = Field(
        False,
        description="The default value of this parameter is False. If the "
        "specified target path is directory then its value should "
        "be True.",
    )
    overwrite: bool = Field(False, description="Overwrite the destination.")

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.src = os.path.abspath(os.path.expanduser(os.path.expandvars(self.src)))
        self.dst = os.path.abspath(os.path.expanduser(os.path.expandvars(self.dst)))

    def execute(self) -> None:
        if self.overwrite and os.path.islink(self.dst):
            os.symlink(
                self.src,
                ''.join([self.dst, '.tmp']),
                target_is_directory=self.target_is_directory,
            )
            os.rename(self.dst + '.tmp', self.dst)
        elif self.overwrite and os.path.isfile(self.dst):
            os.remove(self.dst)
            os.symlink(
                src=self.src, dst=self.dst, target_is_directory=self.target_is_directory
            )
        else:
            os.symlink(
                src=self.src, dst=self.dst, target_is_directory=self.target_is_directory
            )
