from typing import Union, Optional, Any

from tackle import BaseHook, Field
from tackle.utils.dicts import (
    encode_key_path,
    nested_set,
    get_target_and_key,
    nested_get,
)


class DictUpdateHook(BaseHook, smart_union=True):
    """
    Hook for updating dict objects with values, appending list values, or overwriting
     string / int / float values.
    """

    hook_type: str = 'update'

    # fmt: off
    src: Union[dict, str, list] = Field(
        description="A dict to update and output the result or a str with separators "
                    "or list for a key path to the item update within the context.")
    input: Any = Field(description="The value to update the input `src`.")
    sep: str = Field('/', description="For string src's, a separator for key path.")
    # fmt: on

    args: list = ['src', 'input']

    def exec(self) -> Optional[dict]:
        if isinstance(self.src, (str, list)):
            self.src = encode_key_path(self.src, self.sep)
        if isinstance(self.src, list):
            target_context, set_key_path = get_target_and_key(self, key_path=self.src)

            src = nested_get(
                element=target_context,
                keys=set_key_path,
            )
            if isinstance(src, dict):
                src.update(self.input)
            elif isinstance(src, list):
                src.append(self.input)
            else:
                # This overwrites the input
                nested_set(
                    element=target_context,
                    keys=set_key_path,
                    value=self.input,
                )
        else:
            self.src.update(self.input)
            return self.src
