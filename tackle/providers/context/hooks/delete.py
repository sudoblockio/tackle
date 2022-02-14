from typing import Union

from tackle.models import BaseHook, Field
from tackle.utils.dicts import nested_delete, encode_key_path


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
    _args = ['path']
    # fmt: on

    def execute(self) -> None:
        """Run the hook."""
        self.path = encode_key_path(self.path, self.sep)
        nested_delete(
            element=self.output_dict,
            keys=self.path,
        )
