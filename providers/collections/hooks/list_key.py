from typing import Optional

from tackle import BaseHook, Field


class ListKeyValuesHook(BaseHook):
    """Hook for getting a list of values from a list of maps based on a key."""

    hook_type: str = 'list_key_values'
    # fmt: off
    src: list = Field(
        ..., description="A list to extract the keys out of.", render_by_default=True)
    key: str = Field(...)
    reject_keys: dict = Field(
        None, description="A dict of keys with values to not include in output.")
    src_is_key_path: bool = Field(
        False, description="If the src is a list and is meant to be a key path.")
    sep: str = Field('/', description="For string src's, a separator for key path.")
    # fmt: on

    args: list = ['src', 'key']

    def reject(self, i) -> bool:
        for k, v in self.reject_keys:
            if k in i and i[k] == v:
                return False
        return True

    def exec(self) -> Optional[list]:
        if self.reject_keys is None:
            return [i[self.key] for i in self.src]
        else:
            return [i[self.key] for i in self.src if self.reject(i)]


# class KeyListHook(BaseHook):
#     """Hook for getting an item in a list of maps with a key matching a value."""
#
#     hook_type: str = 'list_key_value'
#     # fmt: off
#     src: Union[list, str] = Field(
#         ..., description="A list to extract the keys out of.")
#     key: str = Field(...)
#     src_is_key_path: bool = Field(
#         False, description="If the src is a list and is meant to be a key path.")
#     sep: str = Field('/', description="For string src's, a separator for key path.")
#     # fmt: on
#
#     args: list = ['src', 'key']
#
#     def exec(self) -> Optional[list]:
#         if isinstance(self.src, list):
#             return [i[self.key] for i in self.src]
#         else:
#             raise NotImplementedError
