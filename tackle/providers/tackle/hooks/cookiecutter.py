# -*- coding: utf-8 -*-

"""Azure hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class CookiecutterHook(BaseHook):
    """Hook for running cookiecutters.

    :return: List of regions
    """

    type: str = 'cookiecutter'

    def execute(self):
        pass
