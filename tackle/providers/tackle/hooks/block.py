"""Block hook."""
from tackle.models import BaseHook, Context


class BlockHook(BaseHook):
    """
    Hook for blocks of hooks.

    This is a special case where the hooks input variables are not rendered
    until it is later executed. Each `item` is looped over and parsed like a
    normal pass. Useful if you have a block of hooks that should be grouped
    into a single conditional / looped execution.

    :param items: Map of inputs
    """

    type: str = 'block'
    items: dict

    _render_exclude = {'items'}

    def execute(self):
        from tackle.parser import walk_sync

        existing_context = self.output_dict.copy()
        existing_context.update(self.existing_context)

        tmp_context = Context(
            providers=self.providers_,
            existing_context=existing_context,
            output_dict={},
            input_dict=self.items,
            key_path=[],
            no_input=self.no_input,
        )
        walk_sync(context=tmp_context, element=self.items.copy())
        return tmp_context.output_dict
