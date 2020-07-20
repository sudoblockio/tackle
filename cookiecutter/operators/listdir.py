# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import os
import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class ListdirOperator(BaseOperator):
    """
    Operator for `listdir`. Lists the contents of a directory.

    :param directory: String for the path to directory
    :param directories: List of paths to directories to list
    :param sort: Boolean to sort the output
    :param ignore_hidden_files: Boolean to ignore hidden files

    :return: A list of contents of the directory
    """

    type = 'listdir'

    def __init__(self, *args, **kwargs):  # noqa
        super(ListdirOperator, self).__init__(*args, **kwargs)

        self.ignore_hidden_files = (
            self.operator_dict['ignore_hidden_files']
            if 'ignore_hidden_files' in self.operator_dict
            else False
        )

    def _execute(self):
        if 'directory' in self.operator_dict:
            files = os.listdir(self.operator_dict['directory'])
            if self.operator_dict['sort'] if 'sort' in self.operator_dict else False:
                files.sort()
            if self.ignore_hidden_files:
                return [f for f in files if not f.startswith('.')]
            else:
                return files

        elif 'directories' in self.operator_dict:
            if isinstance(self.operator_dict['directories'], list):
                # If instance is a list, return a dict with the keys as
                # the items in list
                contents = {}
                for i in self.operator_dict['directories']:
                    contents[i] = os.listdir(i)
                    if (
                        self.operator_dict['sort']
                        if 'sort' in self.operator_dict
                        else False
                    ):
                        contents[i].sort()
                return contents
            else:
                raise ValueError("directories key must be list")
        else:
            raise NotImplementedError(
                "Have not implemented dict input to "
                "`directories` for `type` 'listdir'"
            )
