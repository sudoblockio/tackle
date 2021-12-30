"""String hooks."""
import logging
from typing import List

from tackle.models import BaseHook, Field

logger = logging.getLogger(__name__)


class SplitHook(BaseHook):
    """Hook for splitting a string into as list based on a separator."""

    hook_type: str = 'split'

    input: str = Field(..., description="A list of string to split or just a string")
    separator: str = Field(".", description="String separator")
    _args: list = ['input']

    def execute(self):
        return self.input.split(self.separator)


class JoinHook(BaseHook):
    """Join a list of strings with a separator."""

    hook_type: str = 'join'

    input: List[str] = Field(
        ..., description="A list of strings to join.", render_by_default=True
    )
    separator: str = Field('.', description="String separator.")
    _args: list = ['input']

    def execute(self):
        return self.separator.join(self.input)
