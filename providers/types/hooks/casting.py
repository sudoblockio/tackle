"""Data type hook."""
from typing import Any

from tackle import BaseHook, Field


class IntegerHook(BaseHook):
    """Hook for casting a variable to an integer type."""

    hook_name = 'int'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> int:
        return int(self.input)


class FloatHook(BaseHook):
    """Hook for casting a variable to a float type."""

    hook_name = 'float'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> float:
        return float(self.input)


class BoolHook(BaseHook):
    """Hook for casting a variable to a bool type."""

    hook_name = 'bool'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> bool:
        return bool(self.input)


class StrHook(BaseHook):
    """Hook for casting a variable to a string type."""

    hook_name = 'str'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> str:
        return str(self.input)


class HexHook(BaseHook):
    """Hook for changing an int to a hexidecimal."""

    hook_name = 'hex'
    input: int = Field(..., description="Any variable input.", render_by_default=True)
    args: list = ['input']

    def exec(self) -> hex:
        return hex(self.input)
