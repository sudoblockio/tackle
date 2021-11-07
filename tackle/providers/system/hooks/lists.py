# -*- coding: utf-8 -*-

"""Lists hook."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from typing import List, Union
import re

from tackle import BaseHook, Field
from tackle.utils import literal_type

logger = logging.getLogger(__name__)


class ListAppendHook(BaseHook):
    """Hook for updating dict objects with items."""

    type: str = 'append'
    input: list = Field(..., description="A list append to.")
    item: Union[list, str] = Field(
        ..., description="A list or string to append to `input` list."
    )

    _args: list = ['input', 'item']

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
    :return: A list without removed objects objects.
    """

    type: str = 'list_remove'
    input: list = Field(description="A list to append to.")
    item: Union[list, str] = Field(
        ..., description="A list or string to append to `input` list."
    )

    _args: list = ['input', 'item']

    def execute(self):
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
    keys: list
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
