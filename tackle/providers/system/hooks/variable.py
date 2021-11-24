# -*- coding: utf-8 -*-

"""Variable hook."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import re
from typing import Union, List, Dict, Any
from pydantic import Field

from tackle.models import BaseHook
from tackle.utils import merge_configs

logger = logging.getLogger(__name__)


class VarHook(BaseHook):
    """
    Hook for registering a variable based on an input. Only useful for rendering as
    otherwise you wouldn't need this hook at all.
    """

    type: str = 'var'
    input: Any = Field(..., description="Any variable input.", render_by_default=True)
    remove: Union[str, List] = Field(
        None, description="Parameter or regex to remove from list or dict"
    )
    update: Dict = Field(
        None,
        description="Use the python `update` dict method on `contents` before writing",
    )
    merge_dict: Dict = Field(None, description="Merge a map into a map variable.")

    _args: list = ['input']

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
