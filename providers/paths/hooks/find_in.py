import os
from typing import Any, TYPE_CHECKING
from pydantic import Field

from tackle import BaseHook
from tackle import exceptions

if TYPE_CHECKING:
    from tackle.models_new import Context


def find_in_parent(
        context: 'Context',
        dir: str,
        targets: list,
        fallback=None,
) -> str:
    """Recursively search in parent directories for a path to a target file."""
    for i in os.listdir(dir):
        if i in targets:
            return os.path.abspath(os.path.join(dir, i))

    if os.path.abspath(dir) == '/':
        if fallback:
            return fallback
        else:
            raise exceptions.HookCallException(
                f'The targets={targets} doen\'t exist in the parent directories.',
                context=context,
            )
    return find_in_parent(
        dir=os.path.dirname(os.path.abspath(dir)),
        targets=targets,
        fallback=fallback,
    )


class FindInParentHook(BaseHook):
    """Hook to find the absolute path to a file or directory in parent directories."""

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

    args: list = ['target']

    def exec(self) -> str:
        return find_in_parent(
            context=self.context,
            dir=self.starting_dir,
            targets=[self.target],
            fallback=self.fallback,
        )


class FindInChildHook(BaseHook):
    """Hook to find the absolute path to a file or directory in child directories."""

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

    args: list = ['target']

    def exec(self) -> list:
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.starting_dir):
            files += [
                os.path.join(dirpath, file) for file in filenames if file == self.target
            ]

        if len(files) == 0:
            return self.fallback

        return files
