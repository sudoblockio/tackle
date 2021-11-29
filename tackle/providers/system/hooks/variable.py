"""Variable hook."""
from typing import Any
from pydantic import Field
from tackle.models import BaseHook


class VarHook(BaseHook):
    """
    Hook for registering a variable based on an input. Only useful for rendering as
    otherwise you wouldn't need this hook at all.
    """

    type: str = 'var'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    _args: list = ['input']

    def execute(self):
        return self.input
