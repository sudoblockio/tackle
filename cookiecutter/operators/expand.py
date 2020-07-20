# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from PyInquirer import prompt

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class InquirerExpandOperator(BaseOperator):
    """
    Operator for PyInquirer `expand` type prompt.

    https://github.com/CITGuru/PyInquirer/blob/master/examples/expand.py

    :param message: String message to show when prompting.
    :param choices: A list of strings or list of k/v pairs per above description
    :param name: A key to insert the output value to. If not provided defaults
        to inserting into parent key
    :return: List of answers
    """

    type = 'expand'

    def __init__(self, *args, **kwargs):  # noqa
        super(InquirerExpandOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        if not self.no_input:
            if 'name' not in self.operator_dict:
                self.operator_dict.update({'name': 'tmp'})
                return prompt([self.operator_dict])['tmp']
            else:
                return prompt([self.operator_dict])
        elif 'default' in self.operator_dict:
            return self.operator_dict['default']
        else:
            # When no_input then return empty list
            return []
