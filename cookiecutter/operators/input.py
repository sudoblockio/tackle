# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from PyInquirer import prompt

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class InquirerInputOperator(BaseOperator):
    """
    Operator for PyInquirer 'input' type prompts.

    :param message: String message to show when prompting.
    :param choices: A list of strings or list of k/v pairs per above description
    :param name: A key to insert the output value to. If not provided defaults to
        inserting into parent key
    :return: String answer
    """

    type = 'input'

    def __init__(self, *args, **kwargs):  # noqa
        super(InquirerInputOperator, self).__init__(*args, **kwargs)
        # default = (
        #     str(self.operator_dict['default'])
        #     if 'default' in self.operator_dict
        #     else None
        # )

    def _execute(self):
        if not self.no_input:
            if 'name' not in self.operator_dict:
                self.operator_dict.update({'name': 'tmp'})
                return prompt([self.operator_dict])['tmp']
            else:
                return prompt([self.operator_dict])
        elif 'default' in self.operator_dict:
            return self.default
        else:
            # When no_input then return empty list
            return []
