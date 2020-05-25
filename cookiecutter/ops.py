# -*- coding: utf-8 -*-

"""Functions for discovering and executing various cookiecutter operators."""

# from operators import *
# from operators import BaseOperator


# class Operators(object):
#     """Hook object."""
#
#     def __init__(self):
#         """Initialize Hook object."""
#         self.operators: list = BaseOperator.__subclasses__()
#         self.types: list = self.__types()
#         print()
#
#     def __types(self):
#         types = list()
#         for h in self.operators:
#             types = types + h.types
#         return types


# def run_operator(operator_dict):
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
