# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class SplitOperator(BaseOperator):
    """
    Operator for PyInquirer type prompts.

    :param input: A list of string to split or just a string
    :param separator: String separator
    :return: List of lists if `input` is list otherwise list
    """

    type = 'split'

    def __init__(self, *args, **kwargs):  # noqa
        super(SplitOperator, self).__init__(*args, **kwargs)

        self.separator = (
            self.operator_dict['separator']
            if 'separator' in self.operator_dict
            else "."
        )

    def _execute(self):
        if isinstance(self.operator_dict['input'], str):
            # If item is a string then return a list
            return self.operator_dict['input'].split(self.separator)
        elif isinstance(self.operator_dict['input'], list):
            # If input is a list then return a nested list
            output = []
            for i in self.operator_dict['input']:
                output.append(i.split(self.separator))
            return output
        else:
            raise NotImplementedError(
                "Have not implemented dict `input` for `type` 'split'"
            )


class JoinOperator(BaseOperator):
    """
    Operator for PyInquirer type prompts.

    :param input: A list of string to join
    :param separator: String separator
    :return: String
    """

    type = 'join'

    def __init__(self, *args, **kwargs):  # noqa
        super(JoinOperator, self).__init__(*args, **kwargs)

        self.input = self.operator_dict['input']
        self.separator = (
            self.operator_dict['separator']
            if 'separator' in self.operator_dict
            else "."
        )

    def _execute(self):
        if isinstance(self.input, str):
            # If item is a string then return a list
            raise ValueError("Input must be list")
        elif isinstance(self.input, list):
            # If input is a list then return a nested list
            return self.separator.join(self.input)
        else:
            raise NotImplementedError(
                "Have not implemented dict `input` for `type` 'join'"
            )
