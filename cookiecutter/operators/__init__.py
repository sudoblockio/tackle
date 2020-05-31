# -*- coding: utf-8 -*-

"""Functions for generating a project from a project template."""
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod
from os import listdir
from os.path import dirname, basename

__all__ = [
    basename(f)[:-3]
    for f in listdir(dirname(__file__))
    if f[-3:] == ".py" and not f.endswith("__init__.py")
]


class BaseOperator(metaclass=ABCMeta):
    """Base hook mixin class."""

    def __init__(self, operator_dict, context=None):
        """Initialize Basehook."""
        self.operator_dict = operator_dict
        self.context = context or {}

    @abstractmethod
    def execute(self):
        pass
