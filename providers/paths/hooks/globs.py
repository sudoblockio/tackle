import sys
import glob

from tackle.models import BaseHook, Field
from tackle import exceptions

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context


def raise_version_error_msg(field_name, version: int, context: 'Context'):
    raise exceptions.HookCallException(
        f"The field={field_name} in the glob hook not available in version 3.{version}",
        context=context,
    ) from None


class GlobHook(BaseHook):
    """
    Hook for running python's glob module. Return a possibly empty list of path names
     that match pathname, which must be a string containing a path specification.
    """

    hook_type: str = 'glob'
    pathname: str = Field(..., description="The path to file or directory")
    root_dir: str = Field(None, description="The root dir to run glob from.")
    dir_fd: int = Field(
        None,
        description="Similar to root_dir, but it specifies the root directory as an "
        "open directory descriptor instead of a path",
    )
    recursive: bool = Field(False, description="Search underlying directories.")
    include_hidden: bool = Field(False, description="Include hidden files / dirs.")

    args: list = ['pathname']

    def exec(self) -> list:
        options = {
            'recursive': self.recursive,
        }

        if sys.version_info.major >= 10:
            options['root_dir'] = self.root_dir
            options['dir_fd'] = self.dir_fd
        else:
            if self.root_dir is not None:
                raise_version_error_msg('root_dir', 10, self)
            if self.dir_fd is not None:
                raise_version_error_msg('dir_fd', 10, self)

        if sys.version_info.major >= 11:
            options['include_hidden'] = self.include_hidden
        else:
            if self.include_hidden:
                raise_version_error_msg('include_hidden', 11, self)

        return glob.glob(
            self.pathname,
            **options,
        )
