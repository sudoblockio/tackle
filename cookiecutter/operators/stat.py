# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class StatOperator(BaseOperator):
    """Operator for registering a variable based on an input. Useful with rendering."""

    type = 'stat'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize operator."""  # noqa
        super(StatOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )

    def execute(self):
        """."""  # noqa
        return self.operator_dict['input']
