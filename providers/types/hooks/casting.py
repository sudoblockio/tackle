"""Data type hook."""
from typing import Any
from pydantic import Field
from tackle.models import BaseHook


class IntegerHook(BaseHook):
    """Hook for casting a variable to an integer type."""

    hook_type: str = 'int'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> int:
        return int(self.input)


class FloatHook(BaseHook):
    """Hook for casting a variable to a float type."""

    hook_type: str = 'float'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> float:
        return float(self.input)


class BoolHook(BaseHook):
    """Hook for casting a variable to a bool type."""

    hook_type: str = 'bool'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> bool:
        return bool(self.input)


class StrHook(BaseHook):
    """Hook for casting a variable to a string type."""

    hook_type: str = 'str'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> str:
        return str(self.input)
