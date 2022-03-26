import os
from typing import Any

from pydantic import Field

from tackle import BaseHook
from tackle.utils.paths import find_in_parent


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
            dir=self.starting_dir, targets=[self.target], fallback=self.fallback
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
