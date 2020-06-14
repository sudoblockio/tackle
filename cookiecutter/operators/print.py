# -*- coding: utf-8 -*-

"""Functions for generating a project from a project template."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from pprint import pprint

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class PrintOperator(BaseOperator):
    """Operator for PyInquirer type prompts."""

    type = 'print'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize PyInquirer Hook."""  # noqa
        super(PrintOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )

    def execute(self):
        """Run the prompt."""  # noqa
        print(self.operator_dict['statement'])
        return self.operator_dict['statement']


class PprintOperator(BaseOperator):
    """Operator for PyInquirer type prompts."""

    type = 'pprint'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize PyInquirer Hook."""  # noqa
        super(PprintOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )

    def execute(self):
        """Run the prompt."""  # noqa
        pprint(self.operator_dict['statement'])
        return self.operator_dict['statement']
