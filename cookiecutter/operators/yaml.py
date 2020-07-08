# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import yaml
from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class YamlOperator(BaseOperator):
    """Operator for yaml."""

    type = 'yaml'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize yaml operator."""  # noqa
        super(YamlOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )
        # Defaulting to run inline
        self.post_gen_operator = (
            self.operator_dict['delay'] if 'delay' in self.operator_dict else False
        )

    def execute(self):
        """
        Execute the yaml operator.

        :param path: The file path to put read or write to
        :param contents: Supplied dictionary or list to write.
        :param mode: The mode that the file should write. Defaults to write 'w'.
            Seee https://docs.python.org/3/library/functions.html#open
        """
        if 'contents' in self.operator_dict:
            mode = self.operator_dict['mode'] if 'mode' in self.operator_dict else 'w'
            with open(self.operator_dict['path'], mode) as f:
                yaml.dump(self.operator_dict['contents'], f)

        else:
            mode = self.operator_dict['mode'] if 'mode' in self.operator_dict else 'r'
            with open(self.operator_dict['path'], mode) as f:
                return yaml.safe_load(f)
