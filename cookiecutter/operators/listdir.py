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

    :param path: String or list to directories to list
    :param sort: Boolean to sort the output
    :param ignore_hidden_files: Boolean to ignore hidden files

    :return: A list of contents of the `path` if input is string,
        A map with keys of items if input `path` is list.
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
        if isinstance(self.operator_dict['path'], str):
            files = os.listdir(os.path.expanduser(self.operator_dict['path']))
            if self.operator_dict['sort'] if 'sort' in self.operator_dict else False:
                files.sort()
            if self.ignore_hidden_files:
                return [f for f in files if not f.startswith('.')]
            else:
                return files

        if isinstance(self.operator_dict['path'], list):
            contents = {}
            for i in self.operator_dict['path']:
                contents[i] = os.listdir(os.path.expanduser(i))
                if (
                    self.operator_dict['sort']
                    if 'sort' in self.operator_dict
                    else False
                ):
                    contents[i].sort()
            return contents

        else:
            raise NotImplementedError(
                "Have not implemented dict input to "
                "`directories` for `type` 'listdir'"
            )
