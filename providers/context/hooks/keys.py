from typing import Union, Optional

from tackle import BaseHook, Field
from tackle.utils.dicts import encode_key_path, nested_get, get_target_and_key


class DictKeysHook(BaseHook):
    """Hook for returning the keys of a dict as a list."""

    hook_type: str = 'keys'

    # fmt: off
    src: Union[dict, str, list] = Field(
        description="A dict to get the keys from and output the result or a str with separators or list for a key path to the element to get the keys from within the context.")
    sep: str = Field('/', description="For string src's, a separator for key path.")
    # fmt: on

    args: list = ['src']

    def exec(self) -> Optional[list]:
        """Convert to list then look up before lifting keys off a dict."""
        key_path = None
        if isinstance(self.src, str):
            key_path = encode_key_path(self.src, self.sep)
        elif isinstance(self.src, list):
            key_path = self.src

        if key_path is not None:
            target_context, trim_key_path = get_target_and_key(self, key_path=key_path)

            self.src = nested_get(
                element=target_context,
                keys=trim_key_path,
            )

        return list(self.src.keys())
