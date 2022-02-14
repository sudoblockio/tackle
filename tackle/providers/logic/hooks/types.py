"""Data type hook."""
from typing import Any
from pydantic import Field
from tackle.models import BaseHook


class TypeHook(BaseHook):
    """Hook for getting the type of a variable."""

    hook_type: str = 'type'

    input: Any = Field(..., description="Any variable input.", render_by_default=True)

    _args: list = ['input']

    def execute(self) -> str:
        return type(self.input).__name__
