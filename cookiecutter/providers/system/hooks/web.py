# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import webbrowser
from pydantic import AnyUrl

from cookiecutter.models import BaseHook

logger = logging.getLogger(__name__)


class WebBrowserOperator(BaseHook):
    """
    Operator for registering a variable based on an input. Useful with rendering.

    :param url: String url to open in browser.
    :return: None
    """

    type: str = 'webbrowser'
    url: AnyUrl

    def execute(self):
        webbrowser.open(self.url, new=2)
