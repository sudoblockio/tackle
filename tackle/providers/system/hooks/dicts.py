# -*- coding: utf-8 -*-

"""Dict hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from typing import Union, Dict, List

from tackle.models import BaseHook
from tackle.utils import merge_configs

logger = logging.getLogger(__name__)


class DictUpdateHook(BaseHook):
    """
    Hook  for updating dict objects with items.

    :param src: The input dict to update
    :param input: A dict or list of dicts to update the input `src`
    :return: An updated dict object.
    """

    type: str = 'update'

    input: Union[Dict, List[Dict]]
    src: Dict

    def execute(self):
        if isinstance(self.input, list):
            for i in self.input:
                self.src.update(i)
        else:
            self.src.update(self.input)

        return self.src


class DictMergeHook(BaseHook):
    """
    Hook  for recursively merging dict objects with input maps.

    :param src: The input dict to update
    :param input: A dict or list of dicts to update the input `dict`
    :return: An updated dict object.
    """

    type: str = 'merge'
    input: Union[Dict, List[Dict]]
    src: Dict

    def execute(self):
        if isinstance(self.input, list):
            for i in self.input:
                self.src = merge_configs(self.src, i)
            return self.src
        else:
            return merge_configs(self.src, self.input)


class DictPopHook(BaseHook):
    """
    Hook  for recursively merging dict objects with input maps.

    :param src: The input dict to update
    :param item: A list or string of items to remove from a dictionary or list
    :return: An updated dict object.
    """

    type: str = 'pop'

    item: Union[Dict, List[str], str]
    src: Dict

    def execute(self):
        if isinstance(self.item, list):
            for i in self.item:
                self.src.pop(i)
            return self.src
        else:
            self.src.pop(self.item)
            return self.src


class DictKeysHook(BaseHook):
    """
    Hook  for returning the keys of a dict.

    :param src: The input dict or list of dicts return the keys for
    :return: List of keys or list of list of keys if input is list
    """

    type: str = 'dict_keys'

    src: Union[Dict, List[Dict]]

    def execute(self):
        if isinstance(self.src, list):
            keys = []
            for i in self.src:
                keys.append(i.keys())
            return keys
        else:
            return self.src.keys()
