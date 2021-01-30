# -*- coding: utf-8 -*-

"""Lists hook."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from typing import List, Union
import re

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class ListAppendHook(BaseHook):
    """
    Hook  for updating dict objects with items.

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


class ListRemoveHook(BaseHook):
    """
    Hook  for updating dict objects with items.

    :param input: A list append to
    :param item: A list or string to remove to `input` list
    :param filter: A regex to remove items from list with
    :return: An removed list list object.
    """

    type: str = 'list_remove'
    input: List
    item: str = None
    items: List = None
    filter: str = None

    def execute(self):
        if self.filter:
            self.input = [i for i in self.input if not re.search(self.filter, i)]
        if self.items:
            self.input = [i for i in self.input if i not in self.items]
        if self.item:
            self.input = [i for i in self.input if i != self.item]
        return self.input


class ListFromDictHook(BaseHook):
    """
    Hook generating a list from a dict based on the keys.

    :param input: A list append to
    :param item: A list or string to append to `input` list
    :return: An appended list object.
    """

    type: str = 'list_from_dict'
    keys: List
    input: dict

    def execute(self):
        return [k for k, _ in self.input.items() if k in self.keys]


class ConcatListsHook(BaseHook):
    """
    Hook to concatenate a list of items.

    :param inputs: A list append to
    :param item: A list or string to append to `input` list
    :return: An appended list object.
    """

    type: str = 'concat'
    input: list

    def execute(self):
        output = None
        for i in self.input:
            output = output + i
        return output
