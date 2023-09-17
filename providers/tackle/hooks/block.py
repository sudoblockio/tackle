from typing import Union

from tackle import BaseHook, Field, Context
from tackle.parser import walk_document


class BlockHook(BaseHook):
    """
    Hook for blocks of hooks. This is a special case where `items` are parsed like a
     normal context with the added benefit of maintaining a `temporary_context` so that
     items on the same level can be accessed in memory / rendered. Normally executed
     via a macro with an arrow. This the only hook the core parser is aware of as it is
     parsing.
    """

    hook_type: str = 'block'
    items: Union[dict, list] = Field(
        ..., description="Items to be parsed like a normal input."
    )

    skip_output: bool = True
    render_exclude: list = ['items']

    def exec(self) -> Union[dict, list]:

        tmp_context = Context(
            # overrides=self.context.data.overrides,
            verbose=self.context.verbose,
            no_input=self.context.no_input,
            key_path=self.context.key_path.copy(),
            key_path_block=self.context.key_path.copy(),
            path=self.context.path,
            data=self.context.data,
            hooks=self.context.hooks,
        )

        walk_document(context=tmp_context, value=self.items.copy())

        return tmp_context.data.public
