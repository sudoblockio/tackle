from typing import Any

from tackle import BaseHook, Context, Field
from tackle.factory import new_context
from tackle.parser import walk_document


class RunHookHook(BaseHook):
    """Hook to run other hooks dynamically."""

    hook_name: str = 'run_hook'
    hook_dict: dict = Field(
        None,
        description="A dict of keys to use with the hook.",
    )

    args: list = ['hook_name', 'hook_dict']
    kwargs: str = 'hook_dict'

    def exec(self, context: 'Context') -> Any:
        # TODO: this can be done more easily if we have a clean way to just call a hook
        #  without having to build a new context. Don't need to assemble if we just have
        #  a simple hook call function.
        element = {'tmp': {context.key_path[-1]: self.hook_name, **self.hook_dict}}

        tmp_context = new_context(
            _hooks=context.hooks,
            existing_data=context.data.public,
        )
        tmp_context.key_path = ['->']
        tmp_context.key_path_block = ['->']
        tmp_context.hooks.public.update(context.hooks.public)
        tmp_context.hooks.private.update(context.hooks.private)

        walk_document(context=tmp_context, value=element)

        return tmp_context.data.public['tmp']
