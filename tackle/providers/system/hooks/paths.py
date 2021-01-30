# # -*- coding: utf-8 -*-

"""Path hooks."""
from __future__ import unicode_literals
from __future__ import print_function

from typing import Any
import logging
import os

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class PathExistsListHook(BaseHook):
    """Hook  for os package 'path_exists' hook.

    :param path: The path to file or directory
    :return: boolean:
    """

    type: str = 'path_exists'
    path: str

    def execute(self):
        return os.path.exists(self.path)


class PathIsdirListHook(BaseHook):
    """
    Hook  for os package 'path_exists' hook.

    :param path: The path to file or directory
    :return: boolean:
    """

    type: str = 'path_isdir'
    path: str

    def execute(self):
        """Run the prompt."""
        return os.path.isdir(self.path)


class FindInParentHook(BaseHook):
    """
    Hook to find the absolute path to a file or directory in parent directories.

    :param target: The name of the file to find the absolute path to
    :param starting_dir: The starting directory to search from. Defaults to current
        working directory.
    :param fallback: String to fallback on if the target is not found.
    :return: string: Absolute path to the target file
    """

    type: str = 'find_in_parent'
    target: str
    fallback: Any
    starting_dir: str = '.'

    def execute(self):
        """Run the prompt."""
        return self._find_in_parent(self.starting_dir)

    def _find_in_parent(self, dir):
        for i in os.listdir(dir):
            if os.path.exists(os.path.join(dir, i)) and i == self.target:
                return os.path.abspath(os.path.join(dir, i))

        if os.path.abspath(dir) == '/':

            if self.fallback:
                return self.fallback
            else:
                raise NotADirectoryError(
                    'The %s target doesn\'t exist in the parent directories.'
                    % self.target
                )
        return self._find_in_parent(dir=os.path.dirname(os.path.abspath(dir)))


class FindInChildHook(BaseHook):
    """
    Hook to find the absolute path to a file or directory in child directories.

    :param target: The name of the file to find the absolute path to
    :param starting_dir: The starting directory to search from. Defaults to current
        working directory.
    :param fallback: String to fallback on if the target is not found.
    :return: string: Absolute path to the target file
    """

    type: str = 'find_in_child'
    target: str
    fallback: Any
    starting_dir: str = '.'

    def execute(self):
        """Run the prompt."""
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.starting_dir):
            files += [os.path.join(dirpath, file) for file
                      in filenames if file == self.target]

        if len(files) == 0:
            return self.fallback

        return files


class PathJoinHook(BaseHook):
    """Hook joining paths.

    :param path: The path to file or directory
    :return: boolean:
    """

    type: str = 'path_join'
    paths: list

    def execute(self):
        return os.path.join(*self.paths)
