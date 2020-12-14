# -*- coding: utf-8 -*-

"""JSON hooks."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import json
from typing import Dict

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class JsonHook(BaseHook):
    """
    Hook  for json.

    If no `contents` is provided, the hook reads from path. Otherwise it writes
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
