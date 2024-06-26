"""Data type hook."""
from typing import Any

from tackle import BaseHook, Field


class TypeHook(BaseHook):
    """Hook for getting the type of a variable."""

    hook_name = 'type'

    input: Any = Field(
        ...,
        description="Any variable input.",
        render_by_default=True,
    )

    args: list = ['input']

    def exec(self) -> str:
        output = type(self.input).__name__
        if output == 'CommentedSeq':
            output = 'list'
        elif output == 'CommentedMap':
            output = 'map'
        return output
