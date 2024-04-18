from typing import Any

from tackle import BaseHook, Context, Field
from tackle.hooks import get_hook_from_context
from tackle.parser import run_hook_exec


class RunHookHook(BaseHook):
    """Hook to run other hooks dynamically."""

    hook_name = 'run_hook'
    hook: str = Field(..., description="The name of the hook to run.")
    hook_dict: dict = Field(
        None,
        description="A dict of keys to use with the hook.",
    )

    args: list = ['hook', 'hook_dict']
    kwargs: str = 'hook_dict'

    def exec(self, context: 'Context') -> Any:
        Hook = get_hook_from_context(context, hook_name=self.hook, args=[], throw=True)
        return run_hook_exec(context, Hook(**self.hook_dict))
