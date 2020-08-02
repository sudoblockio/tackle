# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class ListAppendOperator(BaseOperator):
    """
    Operator for updating dict objects with items.

    :param input: A list append to
    :param item: A list or string to append to `input` list
    :return: An appended list object.
    """

    type = 'append'

    def __init__(self, *args, **kwargs):  # noqa
        super(ListAppendOperator, self).__init__(*args, **kwargs)
        self.input = self.operator_dict['input']
        self.item = self.operator_dict['item']

    def _execute(self):
        if isinstance(self.item, list):
            for i in self.item:
                self.input.append(i)
        else:
            self.input.append(self.item)

        return self.input
