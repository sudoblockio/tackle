# -*- coding: utf-8 -*-

"""String hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from typing import Union, List

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class SplitHook(BaseHook):
    """
    Hook  for PyInquirer type prompts.

    :param input: A list of string to split or just a string
    :param separator: String separator
    :return: List of lists if `input` is list otherwise list
    """

    type: str = 'split'
    separator: str = "."
    input: Union[List[str], str]

    def execute(self):
        if isinstance(self.input, str):
            # If item is a string then return a list
            return self.input.split(self.separator)
        elif isinstance(self.input, list):
            # If input is a list then return a nested list
            output = []
            for i in self.input:
                output.append(i.split(self.separator))
            return output


class JoinHook(BaseHook):
    """
    Hook  for PyInquirer type prompts.

    :param input: A list of string to join
    :param separator: String separator
    :return: String
    """

    type: str = 'join'

    separator: str = '.'
    input: List[str]

    def execute(self):
        return self.separator.join(self.input)
