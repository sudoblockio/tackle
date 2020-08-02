# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from cookiecutter.operators import BaseOperator
from cookiecutter.config import merge_configs

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


class DictMergeOperator(BaseOperator):
    """
    Operator for recursively merging dict objects with input maps.

    :param dict: The input dict to update
    :param input: A dict or list of dicts to update the input `dict`
    :return: An updated dict object.
    """

    type = 'merge'

    def __init__(self, *args, **kwargs):  # noqa
        super(DictMergeOperator, self).__init__(*args, **kwargs)
        self.input = self.operator_dict['input']
        self.dict = self.operator_dict['dict']

    def _execute(self):
        if isinstance(self.input, list):
            for i in self.input:
                self.dict = merge_configs(self.dict, i)
            return self.dict
        else:
            return merge_configs(self.dict, self.input)


class DictPopOperator(BaseOperator):
    """
    Operator for recursively merging dict objects with input maps.

    :param dict: The input dict to update
    :param item: A list or string of items to remove from a dictionary or list
    :return: An updated dict object.
    """

    type = 'pop'

    def __init__(self, *args, **kwargs):  # noqa
        super(DictPopOperator, self).__init__(*args, **kwargs)
        self.dict = self.operator_dict['dict']
        self.item = self.operator_dict['item']

    def _execute(self):
        if isinstance(self.item, list):
            for i in self.item:
                self.dict.pop(i)
            return self.dict
        else:
            self.dict.pop(self.item)
            return self.dict
