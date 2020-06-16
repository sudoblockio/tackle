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
        self.ignore_hidden_files = (
            self.operator_dict['ignore_hidden_files']
            if 'ignore_hidden_files' in self.operator_dict
            else False
        )

    def execute(self):
        """Run the operator."""  # noqa
        if 'directory' in self.operator_dict:
            files = os.listdir(self.operator_dict['directory'])
            if self.ignore_hidden_files:
                return [f for f in files if not f.startswith('.')]
            else:
                return files

        elif isinstance(self.operator_dict['directories'], list):
            # If instance is a list, return a dict with the keys as the items in list
            contents = {}
            for i in self.operator_dict['directories']:
                contents[i] = os.listdir(i)
            return contents
        else:
            raise NotImplementedError(
                "Have not implemented dict input to "
                "`directories` for `type` 'listdir'"
            )
