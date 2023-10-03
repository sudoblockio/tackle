from tackle import BaseHook, Field
from tackle import exceptions


class RaiseHook(BaseHook):
    """Hook for raising an error."""

    hook_name: str = 'raise'
    message: str = Field(None, description="A message to show when raising an error.")

    args: list = ['input', 'value']
    _docs_order = 7

    def exec(self):
        if self.message is None:
            self.message = ''

        raise exceptions.HookCallException(self.message, context=self)
