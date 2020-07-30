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
    :param input: A dict or list of dicts to update the input `dict`
    :return: An updated dict object.
    """

    type = 'update'

    def __init__(self, *args, **kwargs):  # noqa
        super(DictUpdateOperator, self).__init__(*args, **kwargs)
        self.input = self.operator_dict['input']
        self.dict = self.operator_dict['dict']

    def _execute(self):
        if isinstance(self.input, list):
            for i in self.input:
                self.dict.update(i)
        else:
            self.dict.update(self.input)

        return self.dict
