from typing import Union

from tackle.models import BaseHook, Field
from tackle.utils.dicts import nested_delete, encode_key_path, get_target_and_key


class DeleteKeyHook(BaseHook):
    """
    Hook for getting a key based on a key path which is a list with keys and numbers
     for indexes in a list.
    """

    hook_type: str = 'delete'
    # fmt: off
    path: Union[list, str] = Field(
        ..., description="A list or string with a separator for the path to the value "
                         "you want to update with strings for keys and ints for "
                         "indexes in the list.")
    sep: str = Field('/', description="For string paths, a separator for key path.")
    args: list = ['path']
    # fmt: on

    def exec(self) -> None:
        """Run the hook."""
        target_context, set_key_path = get_target_and_key(
            self, key_path=encode_key_path(self.path, self.sep)
        )

        nested_delete(
            element=target_context,
            keys=set_key_path,
        )
