# -*- coding: utf-8 -*-

"""Operator plugin base class that all __subclassess__ are brought in scope."""
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
    """Base operator mixin class."""

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize BaseOperator."""
        self.operator_dict = operator_dict
        self.context = context or {}
        self.no_input = no_input
        self.post_gen_operator = False

    @abstractmethod
    def execute(self):
        """Run the operator."""
        raise NotImplementedError()
