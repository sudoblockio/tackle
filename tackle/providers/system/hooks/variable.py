# -*- coding: utf-8 -*-

"""Variable hook."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import re
from typing import Union, List, Dict

from tackle.models import BaseHook
from tackle.utils import merge_configs

logger = logging.getLogger(__name__)


class VarHook(BaseHook):
    """
    Hook for registering a variable based on an input. Useful with rendering.

    :param remove: Parameter or regex to remove from list or dict
    :param update: Use the python `update` dict method on `contents` before writing
    :param merge_config: Recursively update the contents before writing.
    :param input: Any type input
    :return: any: Processed input.
    """

    type: str = 'var'

    remove: Union[str, List] = None
    update: Dict = None
    merge_config: bool = None
    input: Union[str, Dict, List]
    merge_dict: Dict = None

    def execute(self):
        if self.remove:
            if isinstance(self.remove, str):
                self._remove_from_contents(self.remove)

            if isinstance(self.remove, list):
                for i in self.remove:
                    self._remove_from_contents(i)

        if self.update:
            self.input.update(self.update)

        if self.merge_dict:
            self.input = merge_configs(self.input, self.merge_dict)

        return self.input

    def _remove_from_contents(self, regex):
        if isinstance(self.input, list):
            self.input = [i for i in self.input if not re.search(regex, i)]
        if isinstance(self.input, dict):
            for k in list(self.input.keys()):
                if re.search(regex, k):
                    self.input.pop(k)


# TODO: Remove this
class StatHook(BaseHook):
    """
    Hook  for registering a variable based on an input. Useful with rendering.

    :param remove: Parameter or regex to remove from list or dict
    :param update: Use the python `update` dict method on `contents` before writing
    :param merge_config: Recursively update the contents before writing.
    :param input: Any type input
    :return: any: Processed input.
    """

    type: str = 'stat'

    remove: Union[str, List] = None
    update: Dict = None
    merge_config: bool = None
    input: Union[str, Dict, List]
    merge_dict: Dict = None

    def execute(self):
        if self.remove:
            if isinstance(self.remove, str):
                self._remove_from_contents(self.remove)

            if isinstance(self.remove, list):
                for i in self.remove:
                    self._remove_from_contents(i)

        if self.update:
            self.input.update(self.update)

        if self.merge_dict:
            self.input = merge_configs(self.input, self.merge_dict)

        return self.input

    def _remove_from_contents(self, regex):
        if isinstance(self.input, list):
            self.input = [i for i in self.input if not re.search(regex, i)]
        if isinstance(self.input, dict):
            for k in list(self.input.keys()):
                if re.search(regex, k):
                    self.input.pop(k)
