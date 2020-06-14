# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from pprint import pprint

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class PrintOperator(BaseOperator):
    """Operator for printing an input and returning the output."""

    type = 'print'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize operator."""  # noqa
        super(PrintOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )

    def execute(self):
        """Print the statement."""
        print(self.operator_dict['statement'])
        return self.operator_dict['statement']


class PprintOperator(BaseOperator):
    """Operator for pretty printing an input and returning the output."""

    type = 'pprint'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize operator."""  # noqa
        super(PprintOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )

    def execute(self):
        """Run the operator."""  # noqa
        pprint(self.operator_dict['statement'])
        return self.operator_dict['statement']
