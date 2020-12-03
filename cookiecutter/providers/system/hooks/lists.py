# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from typing import List, Union

from cookiecutter.models import BaseHook

logger = logging.getLogger(__name__)


class ListAppendOperator(BaseHook):
    """
    Operator for updating dict objects with items.

    :param input: A list append to
    :param item: A list or string to append to `input` list
    :return: An appended list object.
    """

    type: str = 'append'
    input: List
    item: Union[List, str]

    def execute(self):
        if isinstance(self.item, list):
            for i in self.item:
                self.input.append(i)
        else:
            self.input.append(self.item)

        return self.input
