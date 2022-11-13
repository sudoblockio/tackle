from typing import Any
from tackle.models import BaseHook, Field
from tackle.parser import parse_tmp_context


class RunHookHook(BaseHook):
    """Hook to run other hooks dynamically."""

    hook_type: str = 'run_hook'

    hook_name: str = Field(..., description="The name of the hook.")
    hook_dict: dict = Field(None, description="A dict of keys to use with the hook.")

    args: list = ['hook_name', 'hook_dict']
    kwargs: str = 'hook_dict'

    def exec(self) -> Any:
        element = {'tmp': {self.key_path[-1]: self.hook_name, **self.hook_dict}}

        output = parse_tmp_context(self, element, existing_context=self.public_context)
        return output['tmp']
