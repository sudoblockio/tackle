from typing import Any

from tackle import BaseHook, Context, Field
from tackle.utils.data_crud import encode_key_path, get_target_and_key, nested_set


class SetKeyHook(BaseHook):
    """
    Hook for setting a key based on a key path which is a list with keys and numbers
     for indexes in a list.
    """

    hook_name = 'set'
    # fmt: off
    path: Any = Field(..., description="A list or string with a separator for the path to the value you want to update with strings for keys and ints for indexes in the list.")
    value: Any = Field(..., description="The value to update the key with.")
    sep: str = Field('.', description="For string paths, a separator for key path.")
    args: list = ['path', 'value']
    # fmt: on

    skip_output: bool = True

    def exec(self, context: Context):
        """Run the hook."""
        target_context, set_key_path = get_target_and_key(
            context=context,
            key_path=encode_key_path(self.path, self.sep),
        )

        nested_set(
            element=target_context,
            keys=set_key_path,
            value=self.value,
        )
