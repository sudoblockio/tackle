# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

from typing_extensions import Literal
import random
import string
import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class RandomHexOperator(BaseOperator):
    """
    Operator for `random_hex`. Lists the contents of a directory.

    :param length: Number for number of digits - default 8
    :return: String
    """

    type: str = 'random_hex'
    length: int = 8

    def execute(self):
        return ''.join(['%0', str(self.length), 'x']) % random.randrange(
            16 ** self.length
        )


class RandomStringOperator(BaseOperator):
    """
    Operator for `random_string`. Lists the contents of a directory.

    :param case: String, either upper or lower, defaults to lower
    :param length: Number for number of digits - default 8
    :return: String
    """

    type: str = 'random_string'
    case: Literal['upper', 'lower'] = 'upper'
    length: int = 8

    def execute(self):
        if self.case == 'upper':
            return ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=self.length)
            )
        elif self.case == 'lower':
            return ''.join(
                random.choices(string.ascii_lowercase + string.digits, k=self.length)
            )
