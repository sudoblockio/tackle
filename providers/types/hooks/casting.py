"""Data type hook."""
from typing import Any

from tackle import BaseHook, Field


class IntegerHook(BaseHook):
    """Hook for casting a variable to an integer type."""

    hook_name: str = 'int'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> int:
        return int(self.input)


class FloatHook(BaseHook):
    """Hook for casting a variable to a float type."""

    hook_name: str = 'float'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> float:
        return float(self.input)


class BoolHook(BaseHook):
    """Hook for casting a variable to a bool type."""

    hook_name: str = 'bool'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> bool:
        return bool(self.input)


class StrHook(BaseHook):
    """Hook for casting a variable to a string type."""

    hook_name: str = 'str'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> str:
        return str(self.input)
