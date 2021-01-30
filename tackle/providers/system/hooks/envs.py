# -*- coding: utf-8 -*-

"""Environment variable hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import os
import logging
from typing import Union

from tackle.models import BaseHook
from tackle.exceptions import HookCallException

logger = logging.getLogger(__name__)


class EnvironmentVariableHook(BaseHook):
    """
    Hook for setting / getting environment variables.

    Sets with input dict. Gets with input string.

    :param input: Dict for setting and string for getting environment variables
    :param fallback: A fallback for getting.
    :return: input
    """

    type: str = 'env_var'
    input: Union[dict, str]
    fallback: str = None

    def execute(self):
        """Get or set env vars."""
        if self.fallback is not None and isinstance(self.input, dict):
            raise HookCallException("Can't have `fallback` with input of type dict.")

        if isinstance(self.input, dict):
            for k, v in self.input.items():
                os.environ[k] = v
            return self.input

        if isinstance(self.input, str):
            return os.getenv(self.input, self.fallback)
