# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class StatOperator(BaseOperator):
    """
    Operator for registering a variable based on an input. Useful with rendering.

    :param input: Any type input
    """

    type = 'stat'

    def __init__(self, *args, **kwargs):  # noqa
        super(StatOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        return self.operator_dict['input']
