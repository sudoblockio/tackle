"""Print hooks."""
import logging
from pprint import pprint
from typing import Any

from rich import print
from rich.console import Console
from rich.markdown import Markdown

from tackle import BaseHook, Field

logger = logging.getLogger(__name__)


class PrintHook(BaseHook):
    r"""
    Hook  for printing an input and returning the output.

    Follows: https://docs.python.org/3/library/functions.html#print

    print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)
    """

    hook_type: str = 'print'

    objects: Any = Field(None, description="The objects to print.")
    sep: str = Field(' ', description="Separator between printed objects.")
    end: str = Field('\n', description="What to print at the end")
    flush: bool = Field(False, description="No clue.")

    _args: list = ['objects']

    def execute(self):
        print(self.objects, sep=self.sep, end=self.end, flush=self.flush)
        return self.objects


class PprintHook(BaseHook):
    """
    Wraps python pprint builtin.

    https://docs.python.org/3/library/pprint.html#pprint.PrettyPrinter
    """

    hook_type: str = 'pprint'

    objects: Any = None
    indent: int = 1
    width: int = 80
    depth: int = None
    compact: bool = False
    sort_dicts: bool = True
    underscore_numbers: bool = False

    _args: list = ['objects']

    def execute(self):
        pprint(
            self.objects,
            indent=self.indent,
            width=self.width,
            # stream=self.stream,
            compact=self.compact,
            sort_dicts=self.sort_dicts,
            underscore_numbers=self.underscore_numbers,
        )
        return


class MarkdownPrintHook(BaseHook):
    """Hook for printing markdown and returning the output."""

    hook_type: str = 'markdown'
    text: str = None

    _args: list = ['text']

    def execute(self):
        console = Console()
        console.print(Markdown(self.text))
        return self.text
