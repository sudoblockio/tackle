# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import os
from pathlib import Path
import logging
import shutil
from distutils.dir_util import copy_tree

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class CopyOperator(BaseOperator):
    """
    Operator for updating dict objects with items.

    :param src: String or list of sources, either a directories or files
    :param dst: String for path to copy to
    :param create_path: Boolean to create the directory path if it does not exist.
        Defaults to true
    :return: None
    """

    type = 'copy'

    def __init__(self, *args, **kwargs):  # noqa
        super(CopyOperator, self).__init__(*args, **kwargs)
        if isinstance(self.operator_dict['src'], str):
            self.src = os.path.abspath(self.operator_dict['src'])
        if isinstance(self.operator_dict['src'], list):
            self.src = [os.path.abspath(f) for f in self.operator_dict['src']]

        self.dst = os.path.abspath(self.operator_dict['dst'])
        self.create_path = (
            self.operator_dict['create_path']
            if 'create_path' in self.operator_dict
            else True
        )

    def _execute(self):
        if self.create_path:
            if isinstance(self.src, list) and not os.path.isdir(self.dst):
                Path(self.dst).mkdir(parents=True, exist_ok=True)
            elif isinstance(self.src, str) and not os.path.isdir(
                os.path.dirname(self.dst)
            ):
                Path(os.path.basename(self.dst)).mkdir(parents=True, exist_ok=True)
            elif isinstance(self.src, dict):
                raise NotImplementedError

        if isinstance(self.src, str):
            self._copy_file_or_dir(self.src, self.dst)
        elif isinstance(self.src, list):
            for i in self.src:
                self._copy_file_or_dir(i, os.path.join(self.dst, os.path.basename(i)))

        return None

    @staticmethod
    def _copy_file_or_dir(source, dest):
        if os.path.isdir(source):
            copy_tree(source, dest)
        elif os.path.isfile(source):
            shutil.copyfile(source, dest)
