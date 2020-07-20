# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class DictUpdateOperator(BaseOperator):
    """
    Operator for updating dict objects with items.

    :param dict: The input dict to update
    :param input: A dict to update the input `dict`
    :param inputs: A list of dicts to update `dict` with
    :return: An updated dict object.
    """

    type = 'update'

    def __init__(self, *args, **kwargs):  # noqa
        super(DictUpdateOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        if 'inputs' in self.operator_dict:
            for i in self.operator_dict['inputs']:
                self.operator_dict['dict'].update(i)
        if 'input' in self.operator_dict:
            self.operator_dict['dict'].update(self.operator_dict['input'])

        return self.operator_dict['dict']
