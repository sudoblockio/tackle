"""Assert hook."""
from typing import Any

from tackle.models import BaseHook, Field
from tackle import exceptions


class AssertHook(BaseHook):
    """Hook for asserting an input is equal to a value."""

    hook_type: str = 'assert'
    input: Any = Field(..., description="The input - ie right hand side of assert.")
    value: Any = Field(None, description="The value - ie left hand side of assert.")
    exit_on_failure: bool = Field(
        True, description="Whether to exit on assertion error."
    )

    args: list = ['input', 'value']
    _docs_order = 5

    def exec(self) -> bool:
        """Runs for both if the value is present or full assertion."""
        if self.value is None:
            if not self.exit_on_failure:
                try:
                    assert self.input
                    return True
                except AssertionError:
                    return False
            else:
                try:
                    assert self.input
                    return True
                except AssertionError:
                    raise exceptions.HookCallException(
                        f"Error asserting {self.input}=={self.value}", context=self
                    ) from None
        else:
            if not self.exit_on_failure:
                try:
                    assert self.input == self.value
                    return True
                except AssertionError:
                    return False
            else:
                try:
                    assert self.input == self.value
                    return True
                except AssertionError:
                    raise exceptions.HookCallException(
                        f"Error asserting {self.input}=={self.value}", context=self
                    ) from None
