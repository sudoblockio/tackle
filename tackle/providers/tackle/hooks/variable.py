"""Variable hook."""
from typing import Any
from pydantic import Field
from tackle.models import BaseHook


class VarHook(BaseHook):
    """Hook for rendering a variable based on an input. Only useful for rendering as
    otherwise you wouldn't need this hook at all.

    Alternatively just use:

    ```yaml
    key->: {{some_other_key}}
    ```

    Which under the hood is just rewriting the input before processing as this:

    ```yaml
    key->: var "{{some_other_key}}"
    ```

    For unrendered values you would omit any hook logic.
    """

    hook_type: str = 'var'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    _args: list = ['input']

    def _render_var(self, input):
        from tackle.render import render_variable

        output = render_variable(self, input)
        if output == input:
            return output
        else:
            return self._render_var(output)

    def execute(self):
        return self._render_var(self.input)


class TypeHook(BaseHook):
    """Hook for getting the type of a variable."""

    hook_type: str = 'type'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    _args: list = ['input']

    def execute(self):
        return type(self.input)
