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

    hook_type: str = 'block2'
    items: Union[dict, list] = Field(
        ..., description="Items to be parsed like a normal input."
    )

    skip_output: bool = True
    _render_exclude = {'items'}

    def exec(self) -> Union[dict, list]:
        if self.temporary_context is None:
            self.temporary_context = {}

        tmp_context = Context(
            input_context=self.items,
            public_hooks=self.public_hooks,
            private_hooks=self.private_hooks,
            public_context=self.public_context,
            private_context=self.private_context,
            temporary_context=self.temporary_context,
            existing_context=self.existing_context,
            key_path=self.key_path.copy(),
            key_path_block=self.key_path.copy(),
            no_input=self.no_input,
            calling_directory=self.calling_directory,
            calling_file=self.calling_file,
            verbose=self.verbose,
            override_context=self.override_context,
        )



        walk_document(context=tmp_context, value=self.items.copy())

        return self.public_context
