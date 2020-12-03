# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import json
from typing import Dict

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class JsonOperator(BaseOperator):
    """
    Operator for json.

    If no `contents` is provided, the operator reads from path. Otherwise it writes
    the `contents`.

    :param contents: A dict to write
    :param path: The path to write the file
    :return: When writing, returns path. When reading, returns dict
    """

    type: str = 'json'

    contents: Dict = None
    path: str

    def execute(self):
        if self.contents:
            with open(self.path, 'w') as f:
                json.dump(self.contents, f)
            return self.path

        else:
            with open(self.path, 'r') as f:
                return json.load(f)
