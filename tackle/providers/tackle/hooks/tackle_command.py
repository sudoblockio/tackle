# -*- coding: utf-8 -*-

"""Tackle hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class TackleHook(BaseHook):
    """
    Hook for creating tackle commands.
    """

    type: str = 'tackle_command'

    def execute(self):
        pass
