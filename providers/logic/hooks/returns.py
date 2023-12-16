from typing import Any

from tackle import BaseHook, Field, Context


class ReturnHook(BaseHook):
    """
    Hook for stopping parsing and returning a given value instead of the public context
     data. Hooks into parser.py logic by setting the context.break_ = True so that it
     stops parsing the context. Also overwrites the public data which no longer is
     valid since we are only going to be returning a value.
    """
    hook_name: str = 'return'
    value: Any = Field(None, description="The value to return.")

    args: list = ['value']
    skip_output: bool = True

    _docs_order = 3

    def exec(self, context: Context) -> Any:
        context.break_ = True
        # if isinstance(self.value, (dict, list)):
        #
        # else:
        #     context.data.public = self.value

        context.data.public = self.value

        return self.value
