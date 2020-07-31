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
    :param remove: Parameter or regex to remove from list or dict
    :param update: Use the python `update` dict method on `contents` before writing
    :param update_in_place: Dict input that both reads and writes the contents to yaml
        while merging the `update_in_place` dict.
    :param merge_config: Recursively update the contents before writing.
    :param merge_in_place: Dict input that both reads and writes the contents to yaml
        while merging the `merge_in_place` dict.
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
        self.path = self.operator_dict['path']
        self.merge_dict = (
            self.operator_dict['merge_dict']
            if 'merge_dict' in self.operator_dict
            else None
        )
        self.update_in_place = (
            self.operator_dict['update_in_place']
            if 'update_in_place' in self.operator_dict
            else None
        )
        self.merge_in_place = (
            self.operator_dict['merge_in_place']
            if 'merge_in_place' in self.operator_dict
            else None
        )

    def _execute(self):
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

        contents = self.contents if 'contents' in self.operator_dict else None
        if self.update:
            if isinstance(self.update, dict):
                contents.update(self.update)
            else:
                raise ValueError("`update` param must be dictionary.")

        if self.merge_dict:
            if isinstance(self.merge_dict, dict):
                contents = merge_configs(contents, self.merge_dict)
            else:
                raise ValueError("`merge_dict` param must be dictionary.")

        # We are writing yaml
        if self.update_in_place:
            with open(self.path, 'r') as f:
                update_dict = yaml.safe_load(f)
            update_dict.update(self.update_in_place)
            with open(self.path, 'w') as f:
                yaml.dump(update_dict, f)

        if self.merge_in_place:
            with open(self.path, 'r') as f:
                merge_dict = yaml.safe_load(f)
            merge_dict = merge_configs(merge_dict, self.merge_in_place)
            with open(self.path, 'w') as f:
                yaml.dump(merge_dict, f)

        elif self.contents:
            mode = self.operator_dict['mode'] if 'mode' in self.operator_dict else 'w'
            with open(self.path, mode) as f:
                yaml.dump(contents, f)
                return None

        else:
            mode = self.operator_dict['mode'] if 'mode' in self.operator_dict else 'r'
            with open(self.path, mode) as f:
                return yaml.safe_load(f)

    def _remove_from_contents(self, regex):
        if isinstance(self.contents, list):
            self.contents = [i for i in self.contents if not re.search(regex, i)]
        if isinstance(self.contents, dict):
            for k in list(self.contents.keys()):
                if re.search(regex, k):
                    self.contents.pop(k)
