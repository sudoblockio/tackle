from typing import Any

from tackle import BaseHook, Field


class LiteralHook(BaseHook):
    """Literally return the input."""

    hook_name = 'literal'
    input: Any = Field(..., description="Any variable input.")

    args: list = ['input']

    def exec(self) -> Any:
        return self.input
