# -*- coding: utf-8 -*-

"""Functions for generating a project from a project template."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class StatOperator(BaseOperator):
    """Operator for PyInquirer type prompts."""

    type = 'stat'

    def __init__(self, operator_dict, context=None):
        """Initialize PyInquirer Hook."""  # noqa
        super(StatOperator, self).__init__(operator_dict=operator_dict, context=context)

    def execute(self):
        """."""  # noqa
        return self.operator_dict['input']
