# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class SplitOperator(BaseOperator):
    """Operator for PyInquirer type prompts."""

    type = 'split'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize operator."""
        super(SplitOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )
        # Defaulting to run inline
        self.post_gen_operator = (
            self.operator_dict['delay'] if 'delay' in self.operator_dict else False
        )
        self.separator = (
            self.operator_dict['separator']
            if 'separator' in self.operator_dict
            else "."
        )

    def execute(self):
        """Run the operator."""  # noqa
        if isinstance(self.operator_dict['items'], str):
            # If item is a string then return a list
            return self.operator_dict['items'].split(self.separator)
        elif isinstance(self.operator_dict['items'], list):
            # If items is a list then return a nested list
            output = []
            for i in self.operator_dict['items']:
                output.append(i.split('-'))
            return output
        else:
            raise NotImplementedError(
                "Have not implemented dict input to " "`items` for `type` 'split'"
            )
