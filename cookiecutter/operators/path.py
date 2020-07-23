# # -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class PathExistsListOperator(BaseOperator):
    """Operator for os package 'path_exists' operator.

    :param path: The path to file or directory
    :return: boolean:
    """

    type = 'path_exists'

    def __init__(self, *args, **kwargs):  # noqa
        super(PathExistsListOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        return os.path.exists(self.operator_dict['path'])


class PathIsdirListOperator(BaseOperator):
    """
    Operator for os package 'path_exists' operator.

    :param path: The path to file or directory
    :return: boolean:
    """

    type = 'path_isdir'

    def __init__(self, *args, **kwargs):  # noqa
        super(PathIsdirListOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        """Run the prompt."""
        return os.path.isdir(self.operator_dict['path'])


class PathRelativeOperator(BaseOperator):
    """
    Operator to find the absolute path to a file or directory in parent directories.

    :param target: The name of the file to find the absolute path to
    :param starting_dir: The starting directory to search from. Defaults to current
        working directory.
    :return: string: Absolute path to the target file
    """

    type = 'find_in_parent'

    def __init__(self, *args, **kwargs):  # noqa
        super(PathRelativeOperator, self).__init__(*args, **kwargs)

    def _execute(self):
        """Run the prompt."""
        starting_dir = (
            self.operator_dict['starting_dir']
            if 'starting_dir' in self.operator_dict
            else '.'
        )
        return self._find_in_parent(self.operator_dict['target'], starting_dir)

    def _find_in_parent(self, target, dir):
        for i in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, i)) and i == target:
                return os.path.abspath(dir)
            if os.path.isfile(os.path.join(dir, i)) and i == target:
                return os.path.abspath(os.path.join(dir, i))

        if os.path.abspath(dir) == '/':
            raise NotADirectoryError(
                'The %s target doesn\'t exist in the parent directories.' % target
            )
        return self._find_in_parent(target, dir=os.path.dirname(os.path.abspath(dir)))
