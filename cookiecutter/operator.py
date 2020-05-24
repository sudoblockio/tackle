# -*- coding: utf-8 -*-

"""Functions for discovering and executing various cookiecutter operators."""

from cookiecutter.operators import *
from cookiecutter.operators import BaseOperator


class Operators(object):
    """Hook object."""

    def __init__(self):
        """Initialize Hook object."""
        self.operators: list = BaseOperator.__subclasses__()
        self.types: list = self.__types()
        print()

    def __types(self):
        types = list()
        for h in self.operators:
            types = types + h.types
        return types

def run_operator():
    pass
