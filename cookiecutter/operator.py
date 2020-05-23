# -*- coding: utf-8 -*-

"""Functions for discovering and executing various cookiecutter operators."""

from cookiecutter.operators import BaseOperator
from cookiecutter.operators import *  # noqa

class Operators(object):
    """Hook object."""

    def __init__(self):
        """Initialize Hook object."""
        self.hooks: list = BaseOperator.__subclasses__()
        self.types: list = self.__types()

    def __types(self):
        types = list()
        for h in self.hooks:
            types.append(h.type)
        return types