from tackle import BaseHook, Context, Field, exceptions


class RaiseHook(BaseHook):
    """Hook for raising an error."""

    hook_name = 'raise'
    message: str = Field(None, description="A message to show when raising an error.")

    args: list = ['message']
    _docs_order = 7

    def exec(self, context: Context):
        if self.message is None:
            self.message = "Error calling hook."
        raise exceptions.HookCallException(self.message, context=context)
