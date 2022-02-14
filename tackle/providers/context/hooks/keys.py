from typing import Union, Optional

from tackle import BaseHook, Field
from tackle.utils.dicts import encode_key_path, nested_get


class DictKeysHook(BaseHook):
    """Hook for returning the keys of a dict as a list."""

    hook_type: str = 'keys'

    # fmt: off
    src: Union[dict, str, list] = Field(
        description="A dict to get the keys from and output the result or a str with separators or list for a key path to the element to get the keys from within the context.")
    sep: str = Field('/', description="For string src's, a separator for key path.")
    # fmt: on

    _args: list = ['src']

    def execute(self) -> Optional[list]:
        """Convert to list then look up before lifting keys off a dict."""
        if isinstance(self.src, str):
            self.src = encode_key_path(self.src, self.sep)

        if isinstance(self.src, list):
            self.src = nested_get(
                element=self.output_dict,
                keys=self.src,
            )

        return list(self.src.keys())
