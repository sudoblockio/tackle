"""File hooks."""
import os
import random
from pathlib import Path
import logging
import shutil
from distutils.dir_util import copy_tree
from typing import List, Union, Any, Optional

from tackle.models import BaseHook, Field
from tackle.exceptions import HookCallException

logger = logging.getLogger(__name__)


def create_directory_tree(src, dst):
    """Create the file path if it does not exist."""
    if isinstance(src, list) and not os.path.isdir(dst):
        Path(dst).mkdir(parents=True, exist_ok=True)
    elif isinstance(src, str) and not os.path.isdir(os.path.dirname(dst)):
        Path(os.path.basename(dst)).mkdir(parents=True, exist_ok=True)
    elif isinstance(src, dict):
        raise NotImplementedError


def expand_path(path):
    """Expand the path for user."""
    if isinstance(path, str):
        return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))
    if isinstance(path, list):
        return [
            os.path.abspath(os.path.expandvars(os.path.expanduser(f))) for f in path
        ]


class CopyHook(BaseHook):
    """
    Hook coying a file/files or directory/directories to a location.

    :param src: String or list of sources, either a directories or files
    :param dst: String for path to copy to
    :param create_path: Boolean to create the directory path if it does not exist.
        Defaults to true
    :return: None
    """

    hook_type: str = 'copy'
    src: Union[List, str] = Field(
        ..., description="String or list of sources, either a directories or files"
    )
    dst: str = Field(..., description="")
    create_path: bool = True

    _args = ['src', 'dst']

    def __init__(self, **data: Any):
        super().__init__(**data)
        if isinstance(self.src, str):
            self.src = os.path.abspath(os.path.expanduser(self.src))
        if isinstance(self.src, list):
            self.src = [os.path.abspath(os.path.expanduser(f)) for f in self.src]
        # Fix to abs path
        self.dst = os.path.abspath(self.dst)

    def execute(self) -> None:
        if self.create_path:
            create_directory_tree(self.src, self.dst)

        if isinstance(self.src, str):
            self._copy_file_or_dir(self.src, self.dst)
        elif isinstance(self.src, list):
            for i in self.src:
                self._copy_file_or_dir(i, os.path.join(self.dst, os.path.basename(i)))

        return None

    @staticmethod
    def _copy_file_or_dir(source, dest):
        if os.path.isdir(source):
            copy_tree(source, dest)
        elif os.path.isfile(source):
            shutil.copyfile(source, dest)


class MoveHook(BaseHook):
    """
    Hook  for moving a directory or directories to a location.

    :param src: String or list of sources, either directories or files
    :param dst: String for path to copy to
    :param create_path: Boolean to create the directory path if it does not exist.
        Defaults to true
    :return: None
    """

    hook_type: str = 'move'
    src: Union[List, str]
    create_path: bool = True
    dst: str

    _args: list = ['src', 'dst']

    def __init__(self, **data: Any):
        super().__init__(**data)
        if isinstance(self.src, str):
            self.src = os.path.abspath(os.path.expanduser(self.src))
        if isinstance(self.src, list):
            self.src = [os.path.abspath(os.path.expanduser(f)) for f in self.src]
        self.dst = os.path.abspath(self.dst)

    def execute(self) -> None:
        if self.create_path:
            create_directory_tree(self.src, self.dst)

        if isinstance(self.src, str):
            shutil.move(self.src, self.dst)
        elif isinstance(self.src, list):
            for i in self.src:
                shutil.move(i, os.path.join(self.dst, os.path.basename(i)))

        return None


class RemoveHook(BaseHook):
    """
    Hook for removing a directory or directories.

    :param path: String or list of paths to remove
    :return: None
    """

    hook_type: str = 'remove'
    path: Union[List, str]
    fail_silently: bool = False

    _args: list = ['path']

    def __init__(self, **data: Any):
        super().__init__(**data)
        if isinstance(self.path, str):
            self.path = os.path.abspath(os.path.expanduser(self.path))
        if isinstance(self.path, list):
            self.path = [os.path.abspath(os.path.expanduser(f)) for f in self.path]

    def remove_file_or_dir(self, path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        else:
            if not self.fail_silently:
                raise HookCallException(f"Can't find path {path}.")

    def execute(self) -> None:
        if isinstance(self.path, str):
            self.remove_file_or_dir(self.path)
        elif isinstance(self.path, list):
            for i in self.path:
                self.remove_file_or_dir(i)
        return None


# Source: https://codereview.stackexchange.com/questions/186130/file-shredding-secure-deletion-algorithm # noqa
def wipe(f, passes=30):
    """Overwrite a file with bytes."""
    if not os.path.isfile(f):
        return "Could not find the specified file!"
    with open(f, "ba+") as f2w:
        size = f2w.tell()
        for i in range(passes):
            f2w.seek(0)

            f2w.write(os.urandom(size))
    new_name = str(random.randint(1000, 1000000000000))
    os.rename(f, new_name)
    os.remove(new_name)
    return "Success!"


class ShredHook(BaseHook):
    """
    Hook for shredding file/files.

    :param src: String or list of sources, either directories or files
    :param dst: String for path to copy to
    :param create_path: Boolean to create the directory path if it does not exist.
        Defaults to true
    :return: None
    """

    hook_type: str = 'shred'
    src: Union[List, str]
    passes: int = 10

    def __init__(self, **data: Any):
        super().__init__(**data)
        if isinstance(self.src, str):
            self.src = os.path.abspath(os.path.expanduser(self.src))
        if isinstance(self.src, list):
            self.src = [os.path.abspath(os.path.expanduser(f)) for f in self.src]

    def execute(self) -> None:
        if isinstance(self.src, str):
            self.src = [self.src]
        for i in self.src:
            wipe(i, self.passes)


class ChmodHook(BaseHook):
    """
    Hook removing a file or directory.

    :param src: String or list of sources, either directories or files
    :param dst: String for path to copy to
    :param create_path: Boolean to create the directory path if it does not exist.
        Defaults to true
    :return: None
    """

    hook_type: str = 'chmod'
    path: Union[str, list]
    mode: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.path = expand_path(self.path)

    def execute(self) -> None:

        if isinstance(self.path, str):
            self.path = [self.path]
        for i in self.path:
            mode = int(self.mode, 8)
            os.chmod(path=i, mode=mode)

        return None


class CreateFileHook(BaseHook):
    """
    Hook to create an empty file - like touch.

    :param path: String or list of paths to create.
    """

    hook_type: str = 'create_file'
    path: Union[str, list]

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.path = expand_path(self.path)

    def execute(self) -> Union[str, list]:

        if isinstance(self.path, str):
            self.path = [self.path]
        for i in self.path:
            Path(i).touch()

        return self.path


class FileHook(BaseHook):
    """Hook to read and write to a file."""

    hook_type: str = 'file'
    path: str = Field(..., description="Path to read or write file.")
    contents: Any = Field(
        None, description="If writing to file, the contents to write."
    )

    _args = ['path', 'contents']

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.path = expand_path(self.path)

    def execute(self) -> Optional[str]:
        if self.contents is None:
            with open(self.path) as f:
                contents = f.read()
            return contents
        else:
            with open(self.path, 'w') as f:
                f.write(self.contents)
            return
