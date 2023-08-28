from typing import Any

from tackle.models import BaseHook, Field


class ReturnHook(BaseHook):
    """
    Hook for stopping parsing and returning a given value instead of the public context
     data.
    """

    hook_type: str = 'return'
    value: Any = Field(None, description="The value to return.")

    # return_: bool = True
    args: list = ['value']
    skip_output: bool = True

    _docs_order = 3

    def exec(self) -> Any:
        self.context.break_ = True
        self.context.data.public = self.value
        return self.value
