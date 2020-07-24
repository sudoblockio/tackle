# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import re
import warnings

from cookiecutter.operators import BaseOperator
from cookiecutter.config import merge_configs

logger = logging.getLogger(__name__)


class StatOperator(BaseOperator):
    """
    Operator for registering a variable based on an input. Useful with rendering.

    :param remove: Parameter or regex to remove from list or dict
    :param update: Use the python `update` dict method on `contents` before writing
    :param merge_config: Recursively update the contents before writing.
    :param input: Any type input
    :return: any: Processed input.
    """

    type = 'stat'

    def __init__(self, *args, **kwargs):  # noqa
        super(StatOperator, self).__init__(*args, **kwargs)

    def _execute(self):
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

        if 'update' in self.operator_dict:
            if isinstance(self.operator_dict['update'], dict):
                self.operator_dict['input'].update(self.operator_dict['update'])
            else:
                raise ValueError("`update` param must be dictionary.")

        if 'merge_dict' in self.operator_dict:
            if isinstance(self.operator_dict['merge_dict'], dict):
                self.operator_dict['input'] = merge_configs(
                    self.operator_dict['input'], self.operator_dict['merge_dict']
                )
            else:
                raise ValueError("`merge_dict` param must be dictionary.")

        return self.operator_dict['input']

    def _remove_from_contents(self, regex):
        if isinstance(self.operator_dict['input'], list):
            self.operator_dict['input'] = [
                i for i in self.operator_dict['input'] if not re.search(regex, i)
            ]
        if isinstance(self.operator_dict['input'], dict):
            for k in list(self.operator_dict['input'].keys()):
                if re.search(regex, k):
                    self.operator_dict['input'].pop(k)
