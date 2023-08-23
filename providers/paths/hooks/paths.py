import os

from tackle.models import BaseHook, Field


class PathExistsListHook(BaseHook):
    """Hook for os package 'path.exists'."""

    hook_type: str = 'path_exists'
    path: str = Field(..., description="The path to file or directory")

    args: list = ['path']

    def exec(self) -> bool:
        return os.path.exists(self.path)


class PathIsDirListHook(BaseHook):
    """Hook for os package 'path.isdir'."""

    hook_type: str = 'isdir'
    path: str = Field(..., description="The path to a directory")

    args: list = ['path']

    def exec(self) -> bool:
        return os.path.isdir(self.path)


class PathIsFileListHook(BaseHook):
    """Hook for os package 'path.isfile'."""

    hook_type: str = 'isfile'
    path: str = Field(..., description="The path to a file")

    args: list = ['path']

    def exec(self) -> bool:
        return os.path.isfile(self.path)


class PathJoinHook(BaseHook):
    """Hook joining paths."""

    hook_type: str = 'path_join'
    paths: list = Field(
        ...,
        description="List of items in a path to file or directory.",
        render_by_default=True,
    )

    args: list = ['paths']

    def exec(self):
        return os.path.join(*self.paths)


class PathBasenameHook(BaseHook):
    """Hook for getting the basename from a path."""

    hook_type: str = 'basename'
    path: str = Field(
        ...,
        description="Path to the file/directory to get the basename of.",
        render_by_default=True,
    )

    args: list = ['path']

    def exec(self):
        return os.path.basename(self.path)


class PathDirNameHook(BaseHook):
    """Hook for getting the basename from a path."""

    hook_type: str = 'dirname'
    path: str = Field(
        ...,
        description="Path to the file/directory to get the directory name of.",
        render_by_default=True,
    )

    args: list = ['path']

    def exec(self):
        return os.path.dirname(self.path)
