# -*- coding: utf-8 -*-

"""Hook plugin that inherits a base class and is made available through `type`."""
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re
import toml
from typing import Union, Dict, List, Any
import sys
import yubico

from tackle.models import BaseHook
from tackle.utils import merge_configs

logger = logging.getLogger(__name__)


class TomlHook(BaseHook):
    """
    Hook for toml.

    :param path: The file path to put read or write to
    :param contents: Supplied dictionary or list to write.
    :param in_place: Boolean to read the contents of the `path` and then write after
        modifications.
    :param remove: Parameter or regex to remove from list or dict
    :param update: Use the python `update` dict method on `contents` before writing
    :param filter: List or string to values to.
    :param merge_dict: Dict input that recursively overwrites the `contents`.
    :param append_items: List to append to `append_key` key.
    :param append_key: String or list of hierarchical keys to append item to. Defaults
        to root element.
    :param mode: The mode that the file should write. Defaults to write 'w'.
        Seee https://docs.python.org/3/library/functions.html#open
    """

    type: str = 'toml'

    def execute(self):

        try:
            yubikey = yubico.find_yubikey(debug=False)
            print("Version: {}".format(yubikey.version()))
        except yubico.yubico_exception.YubicoError as e:
            print("ERROR: {}".format(e.reason))
            sys.exit(1)
