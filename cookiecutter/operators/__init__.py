# -*- coding: utf-8 -*-

"""Functions for generating a project from a project template."""
from __future__ import unicode_literals

from abc import ABCMeta
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


# def run_operator(operator_dict: dict):
#     # operators = Operators()
# 
#     operator_list = BaseOperator.__subclasses__()
#     for o in operator_list:
#         if operator_dict['type'] in o.types:
#             operator_output = o(operator_dict)
# 
#             print('using %s operator' % operator_dict['type'])
# 
# 
#     operator_output = 1
#     return operator_output