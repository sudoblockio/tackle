# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import re
from typing import Union, List, Dict

from cookiecutter.models import BaseHook
from cookiecutter.utils import merge_configs

logger = logging.getLogger(__name__)


class StatOperator(BaseHook):
    """
    Operator for registering a variable based on an input. Useful with rendering.

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
