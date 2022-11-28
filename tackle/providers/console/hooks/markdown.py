from rich.console import Console
from rich.markdown import Markdown

from tackle import BaseHook, Field


class MarkdownPrintHook(BaseHook):
    """Hook for printing markdown and returning the output."""

    hook_type: str = 'markdown'
    text: str = Field(..., description="The text to render as markdown.")
    justify: str = Field(
        None, description="Justify value for paragraphs. Defaults to None."
    )

    args: list = ['text']

    # TODO: Map this https://rich.readthedocs.io/en/stable/reference/markdown.html?highlight=markdown%20#rich.markdown.Markdown
    # https://github.com/robcxyz/tackle/issues/57
    def exec(self):
        console = Console()
        console.print(Markdown(self.text, justify='left', inline_code_lexer='python'))
        return self.text
