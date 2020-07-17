# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from pprint import pprint

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class PrintOperator(BaseOperator):
    """
    Operator for printing an input and returning the output.

    :param statement: The thing to print
    """

    type = 'print'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize operator."""
        super(PrintOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )

    def execute(self):
        """Print the statement."""
        print(self.operator_dict['statement'])
        return self.operator_dict['statement']


class PprintOperator(BaseOperator):
    """
    Operator for pretty printing an input and returning the output.

    :param statement: The thing to print
    """

    type = 'pprint'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize operator."""
        super(PprintOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )

    def execute(self):
        """Run the operator."""
        pprint(self.operator_dict['statement'])
        return self.operator_dict['statement']
