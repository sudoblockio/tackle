from typing import Any, Optional, Union

from tackle import BaseHook, Context, Field
from tackle.utils.data_crud import encode_key_path, get_target_and_key, nested_get


class AppendHook(BaseHook):
    """Hook for updating dict objects with items."""

    hook_name = 'append'
    # fmt: off
    src: Union[list, str] = Field(
        ..., description="A list append to and output the result or a str with "
                         "separators or list for a key path to the element to append "
                         "to within the context.")
    src_is_key_path: bool = Field(
        False, description="If the src is a list and is meant to be a key path.")
    sep: str = Field('.', description="For string src's, a separator for key path.")
    # item: Union[str, list, dict, int, float, bool] = Field(
    #     ..., description="An item to append to a list."
    # )
    item: Any = Field(
        ..., description="An item to append to a list."
    )
    # fmt: on

    args: list = ['src', 'item']

    def exec(self, context: Context) -> Optional[list]:
        if isinstance(self.src, str) or self.src_is_key_path:
            key_path = encode_key_path(self.src, self.sep)
            # When appending within a block, we try to append to output dict then
            # fallback on trying to append to the existing context
            target_context, set_key_path = get_target_and_key(
                context, key_path=key_path
            )

            # TODO: https://github.com/sudoblockio/tackle/issues/192
            try:
                target = nested_get(
                    element=target_context,
                    keys=set_key_path,
                )
            except KeyError:
                # TODO: This is not ideal - need to nest this and catch errors
                #  Better if we ?
                target = nested_get(
                    element=context.data.temporary,
                    keys=set_key_path,
                )

            target.append(self.item)
            self.skip_output = True
        else:
            self.src.append(self.item)
            return self.src
