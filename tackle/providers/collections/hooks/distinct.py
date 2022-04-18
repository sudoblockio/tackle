from typing import Union, Any, Optional

from tackle import BaseHook, Field
from tackle.utils.dicts import nested_get, encode_key_path


class DistinctHook(BaseHook):
    """Hook for getting distinct items from a list."""

    hook_type: str = 'distinct'
    # fmt: off
    src: Union[list, str] = Field(
        ..., description="A list append to and output the result or a str with "
                         "separators or list for a key path to the element to append "
                         "to within the context.")
    src_is_key_path: bool = Field(
        False, description="If the src is a list and is meant to be a key path.")
    sep: str = Field('/', description="For string src's, a separator for key path.")
    item: Any = Field(
        ..., description="An item to append to a list."
    )
    # fmt: on

    args: list = ['src', 'item']

    def exec(self) -> Optional[list]:
        if isinstance(self.src, str) or self.src_is_key_path:
            self.src = encode_key_path(self.src, self.sep)
            # When appending within a block, we try to append to output dict then
            # fallback on trying to append to the existing context
            try:
                self.src = nested_get(
                    element=self.public_context,
                    keys=self.src,
                )
            except KeyError:
                self.src = nested_get(
                    element=self.existing_context,
                    keys=self.src,
                )
        # TODO: Raise better error if retrieved key path is not a list
        distinct_list = list(set(self.src))
        return distinct_list
