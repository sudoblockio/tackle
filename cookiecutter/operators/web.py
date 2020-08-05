# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import webbrowser

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class WebBrowserOperator(BaseOperator):
    """
    Operator for registering a variable based on an input. Useful with rendering.

    :param url: String url to open in browser.
    :return: None
    """

    type = 'webbrowser'

    def __init__(self, *args, **kwargs):  # noqa
        super(WebBrowserOperator, self).__init__(*args, **kwargs)
        self.url = self.operator_dict['url']

    def _execute(self):
        webbrowser.open(self.url, new=2)
