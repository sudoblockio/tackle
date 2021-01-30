# -*- coding: utf-8 -*-

"""Print hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from pprint import pprint
from typing import Union, Dict, List

from tackle.models import BaseHook
from rich import print
from rich.console import Console
from rich.markdown import Markdown

logger = logging.getLogger(__name__)


class PrintHook(BaseHook):
    """
    Hook  for printing an input and returning the output.

    :param statement: The thing to print
    """

    type: str = 'print'
    statement: Union[Dict, List, str] = None
    out: Union[Dict, List, str] = None
    input: Union[Dict, List, str] = None
    style: str = None

    def execute(self):
        if self.statement:
            print(self.statement)
        if self.out:
            print(self.out)
        if self.input:
            print(self.input)
        return self.statement or self.out or self.input


class PprintHook(BaseHook):
    """
    Hook  for pretty printing an input and returning the output.

    :param statement: The thing to print
    """

    type: str = 'pprint'
    out: Union[Dict, List, str] = None
    input: Union[Dict, List, str] = None
    statement: Union[Dict, List, str] = None

    def execute(self):
        if self.statement:
            pprint(self.statement)
        if self.out:
            pprint(self.out)
        if self.input:
            pprint(self.input)

        return self.statement or self.out or self.input


class MarkdownPrintHook(BaseHook):
    """
    Hook for printing makrdown and returning the output.

    :param statement: The thing to print
    :param out: The thing to print
    :param input: The thing to print
    """

    type: str = 'markdown'
    statement: Union[Dict, List, str] = None
    out: Union[Dict, List, str] = None
    input: Union[Dict, List, str] = None
    style: str = None

    def execute(self):
        console = Console()
        if self.statement:
            console.print(Markdown(self.statement))
        if self.out:
            console.print(Markdown(self.out))
        if self.input:
            console.print(Markdown(self.input))
        return self.statement or self.out or self.input
