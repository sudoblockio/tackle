"""Assert hook."""
from typing import Any

from tackle.models import BaseHook, Field


class AssertHook(BaseHook):
    """Hook for asserting an input is equal to a value."""

    hook_type: str = 'assert'
    input: Any = Field(..., description="The input - ie right hand side of assert.")
    value: Any = Field(None, description="The value - ie left hand side of assert.")
    exit_on_failure: bool = Field(
        True, description="Whether to exit on assertion error."
    )

    _args = ['input', 'value']
    _docs_order = 5

    def execute(self) -> bool:
        """Runs for both if the value is present or full assertion."""
        if self.value is None:
            if not self.exit_on_failure:
                try:
                    assert self.input
                    return True
                except AssertionError:
                    return False
            else:
                assert self.input
                return True
        else:
            if not self.exit_on_failure:
                try:
                    assert self.input == self.value
                    return True
                except AssertionError:
                    return False
            else:
                assert self.input == self.value
                return True
