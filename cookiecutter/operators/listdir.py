# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import os
import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class ListdirOperator(BaseOperator):
    """Operator for PyInquirer type prompts."""

    type = 'listdir'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize operator."""
        super(ListdirOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )
        # Defaulting to run inline
        self.post_gen_operator = (
            self.operator_dict['delay'] if 'delay' in self.operator_dict else False
        )

    def execute(self):
        """Run the operator."""  # noqa
        return os.listdir(self.operator_dict['directory'])
