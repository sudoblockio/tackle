from tackle import BaseHook, Field


class ExitHook(BaseHook):
    """Exit the parser with an exit code."""

    hook_name = 'exit'
    code: int = Field(0, description="The exit code.", render_by_default=True)

    args: list = ['code']

    def exec(self) -> None:
        exit(self.code)
