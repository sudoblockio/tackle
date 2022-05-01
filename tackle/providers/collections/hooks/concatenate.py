from typing import Union, Optional

from tackle import BaseHook, Field


class ConcatenateHook(BaseHook):
    """Hook for getting a list of values from a list of maps."""

    hook_type: str = 'concat'
    # fmt: off
    src: Union[list, str] = Field(
        ..., description="A list to extract the keys out of.", render_by_default=True)
    key: str = Field(...)
    src_is_key_path: bool = Field(
        False, description="If the src is a list and is meant to be a key path.")
    sep: str = Field('/', description="For string src's, a separator for key path.")
    # fmt: on

    args: list = ['src', 'key']

    def exec(self) -> Optional[list]:
        if isinstance(self.src, list):
            return [i[self.key] for i in self.src]
        else:
            raise NotImplementedError
