# -*- coding: utf-8 -*-

"""YAML hook."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import oyaml as yaml
import re
import os

from typing import Union, Dict, List, Any

from tackle.models import BaseHook
from tackle.utils import merge_configs

logger = logging.getLogger(__name__)


class YamlHook(BaseHook):
    """
    Hook  for yaml.

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

    type: str = 'yaml'
    from _collections import OrderedDict

    remove: Union[List, str] = None
    contents: Union[Dict, OrderedDict, List] = None
    update: Dict = None
    filter: List = None
    path: str
    merge_dict: Dict = None
    in_place: bool = False
    append_items: Union[Dict, str, List[Any]] = None
    append_keys: Union[Dict, str, List[Any]] = None
    mode: str = None
    write: bool = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.path = os.path.expanduser(os.path.expandvars(self.path))

    def _load_contents(self):
        if self.contents:
            # We are writing. Context is provided
            self.write = True
            pass
        if self.in_place:
            # We are modifying in place. Context is read from path
            self.write = True
            with open(self.path, 'r') as f:
                self.contents = yaml.safe_load(f)
        elif not self.contents:
            # We are reading. Contents is read from path
            self.write = False
            mode = self.mode or 'r'
            with open(self.path, mode) as f:
                self.contents = yaml.safe_load(f)

    def _append_each_item(self, append_item):
        if isinstance(self.append_keys, str):
            self.contents[self.append_keys].append(append_item)
        elif isinstance(self.append_keys, list):
            for k in self.append_keys[:-1]:
                self.contents = self.contents.setdefault(k, {})
            self.contents[self.append_keys[-1]].append(append_item)
        else:
            self.contents.append(append_item)

    def _remove_from_contents(self, regex):
        if isinstance(self.contents, list):
            self.contents = [i for i in self.contents if not re.search(regex, i)]
        if isinstance(self.contents, dict):
            for k in list(self.contents.keys()):
                if re.search(regex, k):
                    self.contents.pop(k)

    def _modify_dicts(self):
        if self.remove:
            if isinstance(self.remove, str):
                self._remove_from_contents(self.remove)

            if isinstance(self.remove, list):
                for i in self.remove:
                    self._remove_from_contents(i)

        if self.filter:
            if isinstance(self.contents, dict):
                self.contents = {
                    k: v for (k, v) in self.contents.items() if k in self.filter
                }

        if self.update:
            self.contents.update(self.update)

        if self.merge_dict:
            self.contents = merge_configs(self.contents, self.merge_dict)

        if self.append_items:
            if isinstance(self.append_items, str) or isinstance(
                self.append_items, dict
            ):
                self._append_each_item(self.append_items)
            elif isinstance(self.append_items, list):
                for i in self.append_items:
                    self._append_each_item(i)

    def execute(self):
        # Load the path into contents unless it already exists
        self._load_contents()
        # Run all the modifiers
        self._modify_dicts()

        if self.write:
            mode = self.mode or 'w'
            with open(self.path, mode) as f:
                yaml.dump(self.contents, f)
                return self.contents
        else:
            # Read operation, just return contents
            return self.contents
