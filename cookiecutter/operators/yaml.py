# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import yaml
import re
import warnings

from cookiecutter.operators import BaseOperator
from cookiecutter.config import merge_configs

logger = logging.getLogger(__name__)


class YamlOperator(BaseOperator):
    """
    Operator for yaml.

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

    type = 'yaml'

    def __init__(self, *args, **kwargs):  # noqa
        super(YamlOperator, self).__init__(*args, **kwargs)
        self.remove = (
            self.operator_dict['remove'] if 'remove' in self.operator_dict else None
        )
        self.contents = (
            self.operator_dict['contents'] if 'contents' in self.operator_dict else None
        )
        self.update = (
            self.operator_dict['update'] if 'update' in self.operator_dict else None
        )
        self.filter = (
            self.operator_dict['filter'] if 'filter' in self.operator_dict else None
        )
        self.path = self.operator_dict['path']
        self.merge_dict = (
            self.operator_dict['merge_dict']
            if 'merge_dict' in self.operator_dict
            else None
        )
        self.in_place = (
            self.operator_dict['in_place']
            if 'in_place' in self.operator_dict
            else False
        )
        self.append_items = (
            self.operator_dict['append_items']
            if 'append_items' in self.operator_dict
            else None
        )
        self.append_keys = (
            self.operator_dict['append_keys']
            if 'append_keys' in self.operator_dict
            else None
        )

    def _execute(self):
        # Load the path into contents unless it already exists
        self._load_contents()
        # Run all the modifiers
        self._modify_dicts()

        if self.write:
            mode = self.operator_dict['mode'] if 'mode' in self.operator_dict else 'w'
            with open(self.path, mode) as f:
                yaml.dump(self.contents, f)
                return self.contents
        else:
            # Read operation, just return contents
            return self.contents

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
            mode = self.operator_dict['mode'] if 'mode' in self.operator_dict else 'r'
            with open(self.path, mode) as f:
                self.contents = yaml.safe_load(f)

    def _modify_dicts(self):
        if self.remove:
            if isinstance(self.remove, str):
                self._remove_from_contents(self.remove)

            if isinstance(self.remove, list):
                for i in self.remove:
                    self._remove_from_contents(i)

            elif isinstance(self.remove, dict):
                warnings.warn(
                    "Warning: the `remove` parameter can't be a dict - ignored"
                )

        if self.filter:
            self.contents = {
                k: v for (k, v) in self.contents.items() if k in self.filter
            }

        if self.update:
            if isinstance(self.update, dict):
                self.contents.update(self.update)
            else:
                raise ValueError("`update` param must be dictionary.")

        if self.merge_dict:
            if isinstance(self.merge_dict, dict):
                self.contents = merge_configs(self.contents, self.merge_dict)
            else:
                raise ValueError("`merge_dict` param must be dictionary.")

        if self.append_items:
            if isinstance(self.append_items, str) or isinstance(
                self.append_items, dict
            ):
                self._append_each_item(self.append_items)
            elif isinstance(self.append_items, list):
                for i in self.append_items:
                    self._append_each_item(i)

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
