# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from pprint import pprint
from typing import Union, Dict, List

from cookiecutter.models import BaseHook

logger = logging.getLogger(__name__)


class PrintOperator(BaseHook):
    """
    Operator for printing an input and returning the output.

    :param statement: The thing to print
    """

    type: str = 'print'
    statement: Union[Dict, List, str] = None
    out: Union[Dict, List, str] = None

    def execute(self):
        print(self.statement)
        print(self.out)
        return self.statement or self.out


class PprintOperator(BaseHook):
    """
    Operator for pretty printing an input and returning the output.

    :param statement: The thing to print
    """

    type: str = 'pprint'
    statement: Union[Dict, List, str] = None
    out: Union[Dict, List, str] = None

    def execute(self):

        pprint(self.statement)
        pprint(self.out)
        return self.statement or self.out
