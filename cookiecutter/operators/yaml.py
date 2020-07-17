# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import yaml
import re
import warnings

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class YamlOperator(BaseOperator):
    """
    Operator for yaml.

    :param path: The path to read or write to
    :param contents: The contents to write to a file.  If empty the operator then
        reads the path.
    :param remove: List or string of items or regex patterns to remove from list
    :param mode: The mode to read or write the file in
    """

    type = 'yaml'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize yaml operator."""
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
        :param remove: Parameter or regex to remove from list or dict
        :param mode: The mode that the file should write. Defaults to write 'w'.
            Seee https://docs.python.org/3/library/functions.html#open
        """
        if 'remove' in self.operator_dict:
            if isinstance(self.operator_dict['remove'], str):
                self._remove_from_contents(self.operator_dict['remove'])

            if isinstance(self.operator_dict['remove'], list):
                for i in self.operator_dict['remove']:
                    self._remove_from_contents(i)

            elif isinstance(self.operator_dict['remove'], dict):
                warnings.warn(
                    "Warning: the `remove` parameter can't be a dict - ignored"
                )

        if 'contents' in self.operator_dict:
            mode = self.operator_dict['mode'] if 'mode' in self.operator_dict else 'w'
            with open(self.operator_dict['path'], mode) as f:
                yaml.dump(self.operator_dict['contents'], f)
                return None

        else:
            mode = self.operator_dict['mode'] if 'mode' in self.operator_dict else 'r'
            with open(self.operator_dict['path'], mode) as f:
                return yaml.safe_load(f)

    def _remove_from_contents(self, regex):
        if isinstance(self.operator_dict['contents'], list):
            self.operator_dict['contents'] = [
                i for i in self.operator_dict['contents'] if not re.search(regex, i)
            ]
        if isinstance(self.operator_dict['contents'], dict):
            for k in list(self.operator_dict['contents'].keys()):
                if re.search(regex, k):
                    self.operator_dict['contents'].pop(k)
