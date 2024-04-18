from typing import Any

from tackle import BaseHook, Context, Field
from tackle.render import render_string
from tackle.utils.render import wrap_jinja_braces


class ReturnHook(BaseHook):
    """
    Hook for stopping parsing and returning a given value instead of the public context
     data. For strings it renders the value, for dicts / lists it parses it, for
     everything else (bool / int) it returns the value as is.
    """

    hook_name = 'return'
    value: Any = Field(None, description="The value to return.")

    args: list = ['value']
    skip_output: bool = True

    _docs_order = 3

    def exec(self, context: Context) -> Any:
        context.break_ = True
        if isinstance(self.value, (dict, list)):
            # TODO:
            context.data.public = self.value
        elif isinstance(self.value, str):
            context.data.public = render_string(context, wrap_jinja_braces(self.value))
        else:
            context.data.public = self.value

        return self.value


class ReturnsHook(BaseHook):
    """
    Hook for stopping parsing and returning a given value instead of the public context
     data. Returns the value as is without parsing or rendering as compared to the
     `return` hook which renders / parses by default.
    """

    hook_name = 'returns'
    value: Any = Field(None, description="The value to return.")

    args: list = ['value']
    skip_output: bool = True

    _docs_order = 3

    def exec(self, context: Context) -> Any:
        context.break_ = True
        context.data.public = self.value
        return self.value
