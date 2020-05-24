# -*- coding: utf-8 -*-

"""Functions for generating a project from a project template."""
from __future__ import unicode_literals

from __future__ import print_function
from PyInquirer import prompt

from cookiecutter.operators import BaseOperator


class InquirerHook(BaseOperator):
    """Hook for PyInquirer type prompts."""

    types = ['confirm', 'checkbox', 'list', 'password', 'editor']

    def __init__(self, operator_dict, context=None):
        """
        Initialize PyInquirer Hook.

        :param operator_dict:
        :param context:
        """
        super(InquirerHook, self).__init__(operator_dict=operator_dict, context=context)

    def execute(self):
        """
        Run the prompt.

        :return:
        """
        return prompt(self.hook_dict)


# class InquirerConfirm(BaseHook):
#     type = "confirm"
#
#     def __init__(self, hook_dict, context=None):
#         super(InquirerConfirm, self).__init__(hook_dict=hook_dict, context=context)
#
#     def execute(self):
#         return prompt(self.hook_dict)
#
#
# class Checkbox(BaseHook):
#     type = "checkbox"
#
#     def __init__(self, hook_dict, context=None):
#         super(Checkbox, self).__init__(hook_dict=hook_dict, context=context)
#
#     def execute(self):
#         return prompt(self.hook_dict)
#
#
# class InquirerList(BaseHook):
#     type = "list"
#
#     def __init__(self, hook_dict, context=None):
#         super(InquirerList, self).__init__(hook_dict=hook_dict, context=context)
#
#     def execute(self, *args, **kwargs):
#         return prompt(self.hook_dict)
#
#
# class InquirerPassword(BaseHook):
#     type = "password"
#
#     def __init__(self, hook_dict, context=None):
#         super(InquirerPassword, self).__init__(hook_dict=hook_dict, context=context)
#
#     def execute(self, *args, **kwargs):
#         return prompt(self.hook_dict)
#
#
# class InquirerEditor(BaseHook):
#     type = "editor"
#
#     def __init__(self, hook_dict, context=None):
#         super(InquirerEditor, self).__init__(hook_dict=hook_dict, context=context)
#
#     def execute(self, *args, **kwargs):
#         return prompt(self.hook_dict)
