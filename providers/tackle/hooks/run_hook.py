from typing import Any
from tackle import BaseHook, Field
from tackle.hooks import parse_tmp_context


class RunHookHook(BaseHook):
    """Hook to run other hooks dynamically."""

    hook_name: str = 'run_hook'

    hook_name: str = Field(..., description="The name of the hook.")
    hook_dict: dict = Field(None, description="A dict of keys to use with the hook.")

    args: list = ['hook_name', 'hook_dict']
    kwargs: str = 'hook_dict'

    def exec(self) -> Any:
        element = {'tmp': {self.context.key_path[-1]: self.hook_name, **self.hook_dict}}

        output = parse_tmp_context(
            context=self.context,
            element=element,
            existing_context=self.context.data.public,
        )
        return output['tmp']
