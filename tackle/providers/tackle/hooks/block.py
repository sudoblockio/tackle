from typing import Union

from tackle.models import BaseHook, Context, Field
from tackle.parser import walk_sync


class BlockHook(BaseHook):
    """
    Hook for blocks of hooks.
     This is a special case where the hooks input variables are not rendered
     until it is later executed. Each `item` is looped over and parsed like a
     normal pass. Useful if you have a block of hooks that should be grouped
     into a single conditional / looped execution.

    Render context is a little different than normal where both the context
     from outside of the hook and within the hook are made available. See
     [examples](block.md).
    """

    hook_type: str = 'block'
    items: dict = Field(..., description="Items to be parsed like a normal input.")

    _render_exclude = {'items'}

    def execute(self) -> Union[dict, list]:
        existing_context = self.output_dict.copy()
        existing_context.update(self.existing_context)

        tmp_context = Context(
            providers=self.providers,
            existing_context=existing_context,
            output_dict={},
            input_dict=self.items,
            key_path=[],
            no_input=self.no_input,
            calling_directory=self.calling_directory,
            calling_file=self.calling_file,
        )
        walk_sync(context=tmp_context, element=self.items.copy())
        return tmp_context.output_dict
