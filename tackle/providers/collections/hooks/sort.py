from typing import Union, Optional

from tackle import BaseHook, Field


class SortHook(BaseHook):
    """Hook for sorting lists of values or dict by its keys."""

    hook_type: str = 'sort'
    # fmt: off
    src: Union[list, dict] = Field(
        ..., description="A list of strings or a dict with keys to sort.")
    reverse: bool = Field(False, description="To sort in reverse.")
    # TODO: Allow sorting the context based on key path
    # key: str = Field(...)
    # src_is_key_path: bool = Field(
    #     False, description="If the src is a list and is meant to be a key path.")
    # sep: str = Field('/', description="For string src's, a separator for key path.")
    # fmt: on

    args: list = ['src']

    def exec(self) -> Optional[Union[list, dict]]:

        if isinstance(self.src, list):
            # list_type = all(map(lambda x: isinstance(x, str), self.src))
            return self.src.sort()
        else:
            # TODO: Untested
            # https://stackoverflow.com/a/613218/12642712
            sorted_dict = {
                k: v for k, v in sorted(self.src.items(), key=lambda item: item[1])
            }
            return sorted_dict
