from rich.console import Console
from rich.markdown import Markdown

from tackle import BaseHook, Field


class MarkdownPrintHook(BaseHook):
    """Hook for printing markdown and returning the output."""

    hook_type: str = 'markdown'
    text: str = Field(..., description="The text to render as markdown.")

    _args: list = ['text']

    def exec(self):
        console = Console()
        console.print(Markdown(self.text))
        return self.text
