# -*- coding: utf-8 -*-

"""Functions for generating a project from a project template."""
from __future__ import unicode_literals

from os import listdir
from os.path import dirname, basename
from abc import ABCMeta, abstractmethod

__all__ = [
    basename(f)[:-3]
    for f in listdir(dirname(__file__))
    if f[-3:] == ".py" and not f.endswith("__init__.py")
]


class BaseHook(metaclass=ABCMeta):
    """Base hook mixin class."""

    def __init__(self, hook_dict, context=None):
        """Initialize Basehook."""
        self.hook_dict = hook_dict
        self.context = context or {}
        if 'when' in self.hook_dict:

            self.execute_bypass = self.hook_dict['when']
        else:
            self.execute_bypass = False

        if 'loop' in self.hook_dict:
            self.execute_list = self.hook_dict['loop']
        else:
            self.execute_list = []

    @classmethod
    def _execute(cls, prompt, context):
        if not cls(prompt, context=context).execute_bypass:
            return cls.execute()

    @abstractmethod
    def execute(self):
        """
        Execute the hook.

        :return:
        """
        pass
