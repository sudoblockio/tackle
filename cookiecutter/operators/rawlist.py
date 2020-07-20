# # -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from PyInquirer import prompt

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class InquirerListOperator(BaseOperator):
    """
    Operator for PyInquirer 'rawlist' type prompts.

    :param message: String message to show when prompting.
    :param choices: A list of strings or list of k/v pairs per above description
    :param name: A key to insert the output value to. If not provided defaults to
        inserting into parent key
    :return: String for the answer
    """

    type = 'rawlist'

    def __init__(self, *args, **kwargs):  # noqa
        super(InquirerListOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        """Run the prompt."""  # noqa
        if 'name' not in self.operator_dict:
            self.operator_dict.update({'name': 'tmp'})
            return prompt([self.operator_dict])['tmp']
        else:
            return prompt([self.operator_dict])
