# -*- coding: utf-8 -*-

"""Print hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from pprint import pprint
from typing import Union, Dict, List

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class PrintHook(BaseHook):
    """
    Hook  for printing an input and returning the output.

    :param statement: The thing to print
    """

    type: str = 'print'
    statement: Union[Dict, List, str] = None
    out: Union[Dict, List, str] = None

    def execute(self):
        if self.statement:
            print(self.statement)
        if self.out:
            print(self.out)
        return self.statement or self.out


class PprintHook(BaseHook):
    """
    Hook  for pretty printing an input and returning the output.

    :param statement: The thing to print
    """

    type: str = 'pprint'
    statement: Union[Dict, List, str] = None
    out: Union[Dict, List, str] = None

    def execute(self):
        if self.statement:
            pprint(self.statement)
        if self.out:
            pprint(self.out)
        return self.statement or self.out
