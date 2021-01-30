# -*- coding: utf-8 -*-

"""Variable hook."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import re
from typing import Union, List, Dict, Any

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

    # TODO: Figure out what the right constraints are.  Fails tests and casts a
    #  list of lists into a dict for some reason. Any is too loose and
    # input: Union[str, dict, list]
    input: Any

    remove: Union[str, List] = None
    update: Dict = None
    merge_config: bool = None
    merge_dict: Dict = None

    def _remove_from_contents(self, regex):
        if isinstance(self.input, list):
            self.input = [i for i in self.input if not re.search(regex, i)]
        if isinstance(self.input, dict):
            for k in list(self.input.keys()):
                if re.search(regex, k):
                    self.input.pop(k)

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


# TODO: Keep till 0.2+
class StatHook(VarHook, BaseHook):
    """Temporary holder."""
    type: str = 'stat'
