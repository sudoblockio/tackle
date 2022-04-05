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

    # def exec(self) -> Union[dict, list]:
    #     existing_context = self.public_context.copy()
    #     existing_context.update(self.existing_context)
    #
    #     tmp_context = Context(
    #         provider_hooks=self.provider_hooks,
    #         existing_context=existing_context,
    #         public_context={},
    #         input_context=self.items,
    #         key_path=[],
    #         no_input=self.no_input,
    #         calling_directory=self.calling_directory,
    #         calling_file=self.calling_file,
    #     )
    #     walk_sync(context=tmp_context, element=self.items.copy())
    #     return tmp_context.public_context

    def exec(self) -> Union[dict, list]:
        # self.key_path = self.key_path[:-1]
        # if isinstance(self.key_path[-1], bytes):
        # Remove the prior hook from the key path so it does not get used when writing
        if self.key_path[-1] == b'\x00\x00':
            # If the key path is part of a list
            self.key_path.pop(-2)
        elif self.key_path[-1] in ('->', '_>'):
            # Normal
            self.key_path.pop(-1)

        # else:
        #     self.key_path.pop(-1)
        # key_path = self.key_path[:-1]

        # if self.merge:
        #     print()
        #     self.key_path.pop()

        tmp_context = Context(
            provider_hooks=self.provider_hooks,
            existing_context=self.existing_context.copy(),
            public_context=self.public_context,
            input_context=self.items,
            # key_path=self.key_path[:-1],
            key_path=self.key_path.copy(),
            key_path_block=self.key_path.copy(),
            no_input=self.no_input,
            calling_directory=self.calling_directory,
            calling_file=self.calling_file,
            verbose=self.verbose,
        )
        if len(self.key_path) > 0:
            if self.key_path[0] == b'\x00\x01':
                print()

        walk_sync(context=tmp_context, element=self.items.copy())

        # for i in self.key_path[:-1]:
        #     self.public_context = self.public_context[i]

        return self.public_context
