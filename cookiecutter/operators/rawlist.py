# # -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
# from __future__ import unicode_literals
# from __future__ import print_function
#
# import logging
# from PyInquirer import prompt
#
# from cookiecutter.operators import BaseOperator
#
# logger = logging.getLogger(__name__)
#
#
# class InquirerListOperator(BaseOperator):
#     """Operator for PyInquirer 'rawlist' type prompts."""
#
#     type = 'rawlist'
#
#     def __init__(self, operator_dict, context=None, no_input=False):
#         """Initialize PyInquirer operator."""  # noqa
#         super(InquirerListOperator, self).__init__(
#             operator_dict=operator_dict, context=context, no_input=no_input
#         )
#
#     def execute(self):
#         """Run the prompt."""  # noqa
#         if 'name' not in self.operator_dict:
#             self.operator_dict.update({'name': 'tmp'})
#             return prompt([self.operator_dict])['tmp']
#         else:
#             return prompt([self.operator_dict])
