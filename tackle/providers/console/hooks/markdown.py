import logging
from rich.console import Console
from rich.markdown import Markdown

from tackle import BaseHook

logger = logging.getLogger(__name__)


class MarkdownPrintHook(BaseHook):
    """Hook for printing markdown and returning the output."""

    hook_type: str = 'markdown'
    text: str = None

    _args: list = ['text']

    def execute(self):
        console = Console()
        console.print(Markdown(self.text))
        return self.text
