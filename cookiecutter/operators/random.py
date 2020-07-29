# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

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

    type = 'random_hex'

    def __init__(self, *args, **kwargs):  # noqa
        super(RandomHexOperator, self).__init__(*args, **kwargs)
        self.length = (
            self.operator_dict['length'] if 'length' in self.operator_dict else 8
        )

    def _execute(self):
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

    type = 'random_string'

    def __init__(self, *args, **kwargs):  # noqa
        super(RandomStringOperator, self).__init__(*args, **kwargs)
        self.case = (
            self.operator_dict['case'] if 'case' in self.operator_dict else 'upper'
        )
        self.length = (
            self.operator_dict['length'] if 'length' in self.operator_dict else 8
        )

    def _execute(self):
        if self.case == 'upper':
            return ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=self.length)
            )
        elif self.case == 'lower':
            return ''.join(
                random.choices(string.ascii_lowercase + string.digits, k=self.length)
            )
