from typing import Union, Optional, Any

from tackle import BaseHook, Field
from tackle.utils.dicts import encode_key_path, nested_set


class DictUpdateHook(BaseHook, smart_union=True):
    """Hook for updating dict objects with values."""

    hook_type: str = 'update'

    # fmt: off
    src: Union[dict, str, list] = Field(
        description="A dict to update and output the result or a str with separators or list for a key path to the item update within the context.")
    input: Any = Field(description="The value to update the input `src`.")
    sep: str = Field('/', description="For string src's, a separator for key path.")
    # fmt: on

    _args: list = ['src', 'input']

    def __init__(self, **data: Any):
        super().__init__(**data)
        if isinstance(self.src, (str, list)):
            self.src = encode_key_path(self.src, self.sep)

    def execute(self) -> Optional[dict]:
        if isinstance(self.src, list):
            nested_set(
                element=self.output_dict,
                keys=self.src,
                value=self.input,
            )
        else:
            self.src.update(self.input)
            return self.src
