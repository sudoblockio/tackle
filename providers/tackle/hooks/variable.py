from typing import Any

from tackle import BaseHook, Context, Field
from tackle.render import render_variable


class VarHook(BaseHook):
    """
    Hook for rendering a variable based on an input. Only useful for rendering as
     otherwise you wouldn't need this hook at all. Does recursion when the value being
     rendered is still renderable - ie a template within a template.
    """

    hook_name = 'var'
    input: Any = Field(
        ...,
        description="Any variable input.",
        render_by_default=True,
    )
    no_recursion: bool = Field(
        False, description="Don't recursively render embedded templates."
    )

    args: list = ['input']

    def _render_var(self, input: Any, context: 'Context') -> Any:
        output = render_variable(context=context, raw=input)
        if output == input:
            return output
        else:
            return self._render_var(input=output, context=context)

    def exec(self, context: 'Context') -> Any:
        if self.no_recursion:
            # Input is already rendered so only need to pass back
            return self.input
        else:
            return self._render_var(context=context, input=self.input)
