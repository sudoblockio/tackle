from tackle.models import BaseHook, Field


class ExitHook(BaseHook):
    """Exit the parser with an exit code."""

    hook_type: str = 'exit'
    code: int = Field(0, description="The exit code.", render_by_default=True)

    _args: list = ['code']

    def execute(self) -> None:
        exit(self.code)
