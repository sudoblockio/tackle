from typing import Optional, Union

from tackle import BaseHook, Context, Field
from tackle.utils.data_crud import encode_key_path, get_target_and_key, nested_get


class DictValuesHook(BaseHook):
    """Hook for returning the values of a dict as a list."""

    hook_name = 'values'

    # fmt: off
    src: Union[dict, str, list] = Field(
        description="A dict to get the values from and output the result or a str with separators or list for a key path to the element to get the values from within the context.")
    sep: str = Field('.', description="For string src's, a separator for key path.")
    # fmt: on

    args: list = ['src']

    def exec(self, context: Context) -> Optional[list]:
        """Convert to list then look up before lifting values off a dict."""
        key_path = None
        if isinstance(self.src, str):
            key_path = encode_key_path(self.src, self.sep)
        elif isinstance(self.src, list):
            key_path = self.src

        if key_path is not None:
            target_context, trim_key_path = get_target_and_key(
                context=context,
                key_path=key_path,
            )

            self.src = nested_get(
                element=target_context,
                keys=trim_key_path,
            )

        return list(self.src.values())
