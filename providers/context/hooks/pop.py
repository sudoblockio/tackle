from typing import Union

from tackle import BaseHook, Field
from tackle.utils.dicts import encode_key_path, nested_get, get_target_and_key


class DictPopHook(BaseHook):
    """
    Hook for removing (`pop`) a key from a dict or item from a list based on index.
    Follows python's [pop](https://docs.python.org/3/tutorial/datastructures.html)
    """

    hook_name: str = 'pop'

    # fmt: off
    src: Union[dict, str, list] = Field(
        description="A list to remove an item from or dict to remove a key and output "
                    "the result or a str with separators or list for a key path to the "
                    "item operate on within the context.",
    )
    src_is_key_path: bool = Field(False, description="If the src is a list and is meant to be a key path.")
    item: Union[str, int] = Field(
        None,
        description="A string for a key to remove from a dict `src` or integer for an "
                    "index to remove from a list `src`.",
    )
    sep: str = Field('/', description="For string src's, a separator for key path.")
    # fmt: on

    args: list = ['src', 'item']

    def pop_item(self, target):
        if self.item is None:
            target.pop()
        elif isinstance(self.item, list):
            for i in self.item:
                self.src.pop(i)
        else:
            target.pop(self.item)

    def exec(self) -> Union[dict, list, None]:
        """
        Check if the src is a ref to a key in the context or a literal value that will
         be popped.
        """
        if isinstance(self.src, str) or self.src_is_key_path:
            target_context, set_key_path = get_target_and_key(
                self.context, key_path=encode_key_path(self.src, self.sep)
            )
            target = nested_get(
                element=target_context,
                keys=set_key_path,
            )
            self.pop_item(target)
        else:
            self.pop_item(self.src)
            return self.src
