from typing import Any

from pydantic import Field

from tackle import BaseHook
from tackle.utils.dicts import encode_key_path, nested_set


class SetKeyHook(BaseHook):
    """
    Hook for setting a key based on a key path which is a list with keys and numbers
     for indexes in a list.
    """

    hook_type: str = 'set'
    # fmt: off
    path: Any = Field(..., description="A list or string with a separator for the path to the value you want to update with strings for keys and ints for indexes in the list.")
    value: Any = Field(..., description="The value to update the key with.")
    sep: str = Field('/', description="For string paths, a separator for key path.")
    _args = ['path', 'value']
    # fmt: on

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.path = encode_key_path(self.path, self.sep)

    def execute(self):
        """Run the hook."""
        nested_set(
            element=self.output_dict,
            keys=self.path,
            value=self.value,
        )
