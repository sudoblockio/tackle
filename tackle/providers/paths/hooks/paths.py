import os

from tackle.models import BaseHook, Field


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
