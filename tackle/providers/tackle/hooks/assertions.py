"""Assert hook."""
from tackle.models import BaseHook

from typing import Any


class AssertHook(BaseHook):
    """Hook for asserting an input is equal to a value."""

    hook_type: str = 'assert'
    input: Any
    value: Any

    _args = ['input', 'value']

    def execute(self):
        assert self.input == self.value
