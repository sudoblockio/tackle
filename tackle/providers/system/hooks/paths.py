"""Path hooks."""
from typing import Any
import logging
import os

from tackle.models import BaseHook, Field
from tackle.utils.paths import find_in_parent

logger = logging.getLogger(__name__)


class PathExistsListHook(BaseHook):
    """Hook for os package 'path.exists'."""

    hook_type: str = 'path_exists'
    path: str = Field(..., description="The path to file or directory")

    _args: list = ['path']

    def execute(self) -> bool:
        return os.path.exists(self.path)


class PathIsDirListHook(BaseHook):
    """Hook for os package 'path.isdir'."""

    hook_type: str = 'isdir'
    path: str = Field(..., description="The path to a directory")

    _args: list = ['path']

    def execute(self) -> bool:
        return os.path.isdir(self.path)


class PathIsFileListHook(BaseHook):
    """Hook for os package 'path.isfile'."""

    hook_type: str = 'isfile'
    path: str = Field(..., description="The path to a file")

    _args: list = ['path']

    def execute(self) -> bool:
        return os.path.isfile(self.path)


class FindInParentHook(BaseHook):
    """
    Hook to find the absolute path to a file or directory in parent directories.

    :return: string: Absolute path to the target file
    """

    hook_type: str = 'find_in_parent'
    target: str = Field(
        ..., description="The name of the file to find the absolute path to"
    )
    fallback: Any = Field(
        None, description="String to fallback on if the target is not found."
    )
    starting_dir: str = Field(
        '.',
        description="The starting directory to search from. Defaults to current working directory.",
    )

    _args: list = ['target']

    def execute(self):
        return find_in_parent(
            dir=self.starting_dir, targets=[self.target], fallback=self.fallback
        )


class FindInChildHook(BaseHook):
    """
    Hook to find the absolute path to a file or directory in child directories.

    :return: string: Absolute path to the target file
    """

    hook_type: str = 'find_in_child'
    target: str = Field(
        ..., description="The name of the file to find the absolute path to"
    )
    fallback: Any = Field(
        None, description="String to fallback on if the target is not found."
    )
    starting_dir: str = Field(
        '.',
        description="The starting directory to search from. Defaults to current working directory.",
    )

    _args: list = ['target']

    def execute(self):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.starting_dir):
            files += [
                os.path.join(dirpath, file) for file in filenames if file == self.target
            ]

        if len(files) == 0:
            return self.fallback

        return files


class PathJoinHook(BaseHook):
    """Hook joining paths."""

    hook_type: str = 'path_join'
    paths: list = Field(
        ...,
        description="List of items in a path to file or directory.",
        render_by_default=True,
    )

    _args: list = ['paths']

    def execute(self):
        return os.path.join(*self.paths)
