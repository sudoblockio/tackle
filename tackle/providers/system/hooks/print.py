"""Print hooks."""
import logging
from pprint import pprint
from typing import Any, Union, Dict, List

from rich import print
from rich.console import Console
from rich.markdown import Markdown

from tackle import BaseHook, Field

logger = logging.getLogger(__name__)


class PrintHook(BaseHook):
    """
    Hook  for printing an input and returning the output.

    Follows: https://docs.python.org/3/library/functions.html#print

    print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)
    """

    type: str = 'print'

    objects: Any = None
    sep: str = ' '
    end: str = '\n'
    flush: bool = False

    _args: list = ['objects']

    def execute(self):
        print(self.objects, sep=self.sep, end=self.end, flush=self.flush)
        return


class PprintHook(BaseHook):
    """
    Wraps python pprint builtin. https://docs.python.org/3/library/pprint.html#pprint.PrettyPrinter
    """

    type: str = 'pprint'

    objects: Any = None

    indent: int = 1
    width: int = 80
    depth: int = None
    # stream = None
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
    """
    Hook for printing makrdown and returning the output.
    """

    type: str = 'markdown'
    statement: Union[Dict, List, str] = None
    out: Union[Dict, List, str] = None
    input: Union[Dict, List, str] = None
    style: str = None

    _args: list = ['objects']

    def execute(self):
        console = Console()
        if self.statement:
            console.print(Markdown(self.statement))
        if self.out:
            console.print(Markdown(self.out))
        if self.input:
            console.print(Markdown(self.input))
        return self.statement or self.out or self.input
