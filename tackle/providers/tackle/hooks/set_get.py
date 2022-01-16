"""set, get, and delete hooks based on key path."""
from typing import Any

from tackle.utils.dicts import nested_set, nested_get, nested_delete, encode_list_index
from tackle.models import BaseHook, Field


def encode_key_path(path: Any, sep: str) -> list:
    """Encode and key path with bytes for items in a list."""
    if isinstance(path, str):
        path = path.split(sep)
        for i, v in enumerate(path):
            try:
                path[i] = int(v)
            except ValueError:
                pass
        path = [i if not isinstance(i, int) else encode_list_index(i) for i in path]

    # Need to encode keys into bytes as that is how internally the parser works so
    # it doesn't jam up on any integer key. This hook will fail it the key is an
    # int.
    path = [i if not isinstance(i, int) else encode_list_index(i) for i in path]
    if isinstance(path, dict):
        raise NotImplementedError

    return path


class SetKeyHook(BaseHook):
    """
    Hook for setting a key based on a key path which is a list with keys and numbers
    for indexes in a list.
    """

    hook_type: str = 'set_key'
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


class GetKeyHook(BaseHook):
    """
    Hook for getting a key based on a key path which is a list with keys and numbers
    for indexes in a list.
    """

    hook_type: str = 'get_key'
    # fmt: off
    path: Any = Field(..., description="A list or string with a separator for the path to the value you want to update with strings for keys and ints for indexes in the list.")
    sep: str = Field('/', description="For string paths, a separator for key path.")
    _args = ['path']
    # fmt: on

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.path = encode_key_path(self.path, self.sep)

    def execute(self):
        """Run the hook."""
        value = nested_get(
            element=self.output_dict,
            keys=self.path,
        )
        return value


class DeleteKeyHook(BaseHook):
    """
    Hook for getting a key based on a key path which is a list with keys and numbers
    for indexes in a list.
    """

    hook_type: str = 'delete_key'
    # fmt: off
    path: Any = Field(..., description="A list or string with a separator for the path to the value you want to update with strings for keys and ints for indexes in the list.")
    sep: str = Field('/', description="For string paths, a separator for key path.")
    _args = ['path']
    # fmt: on

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.path = encode_key_path(self.path, self.sep)

    def execute(self):
        """Run the hook."""
        nested_delete(
            element=self.output_dict,
            keys=self.path,
        )
