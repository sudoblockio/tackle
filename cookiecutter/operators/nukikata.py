# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import cookiecutter as cc
import logging

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class NukikataOperator(BaseOperator):
    """Operator for calling external cookiecutters."""

    type = 'nukikata'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize operator."""
        super(NukikataOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )
        self.post_gen_operator = (
            self.operator_dict['delay'] if 'delay' in self.operator_dict else False
        )

    def execute(self):
        """Run the nukikata operator."""
        templates = (
            self.operator_dict['templates']
            if 'templates' in self.operator_dict
            else None
        )
        directories = (
            self.operator_dict['directories']
            if 'directories' in self.operator_dict
            else None
        )
        context_files = (
            self.operator_dict['context_files']
            if 'context_files' in self.operator_dict
            else None
        )

        if not templates and not directories and not context_files:
            return self._run_nukikata()

        output = {}
        if templates:
            for i in templates:
                self.operator_dict['template'] = i
                output.update({i: self._run_nukikata()})

        if directories:
            for i in directories:
                self.operator_dict['directory'] = i
                output.update({i: self._run_nukikata()})

        if context_files:
            for i in context_files:
                self.operator_dict['context_file'] = i
                output.update({i: self._run_nukikata()})

        return output

    def _run_nukikata(self):
        output_context = cc.main.cookiecutter(
            template=self.operator_dict['template']
            if 'template' in self.operator_dict
            else '.',
            checkout=self.operator_dict['checkout']
            if 'checkout' in self.operator_dict
            else None,
            no_input=self.no_input,
            context_file=self.operator_dict['context_file']
            if 'context_file' in self.operator_dict
            else None,
            context_key=self.operator_dict['context_key']
            if 'context_key' in self.operator_dict
            else None,
            existing_context=self.operator_dict['existing_context']
            if 'existing_context' in self.operator_dict
            else None,
            extra_context=self.operator_dict['extra_context']
            if 'extra_context' in self.operator_dict
            else None,
            replay=self.operator_dict['replay']
            if 'replay' in self.operator_dict
            else None,
            overwrite_if_exists=self.operator_dict['overwrite_if_exists']
            if 'overwrite_if_exists' in self.operator_dict
            else False,
            output_dir=self.operator_dict['output_dir']
            if 'output_dir' in self.operator_dict
            else '.',
            config_file=self.operator_dict['config_file']
            if 'config_file' in self.operator_dict
            else None,
            default_config=self.operator_dict['default_config']
            if 'default_config' in self.operator_dict
            else False,
            password=self.operator_dict['password']
            if 'password' in self.operator_dict
            else None,
            directory=self.operator_dict['directory']
            if 'directory' in self.operator_dict
            else None,
            skip_if_file_exists=self.operator_dict['skip_if_file_exists']
            if 'skip_if_file_exists' in self.operator_dict
            else False,
        )

        return output_context


class ConfigToNukikataOperator(BaseOperator):
    """Operator for calling external cookiecutters."""

    type = 'obj_to_nuki'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize operator."""
        super(ConfigToNukikataOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )

    def execute(self):
        """Run the nukikata operator."""
        for k, v in self.operator_dict['contents']:
            if isinstance(v, str):

                pass


# # # TODO: Is this needed?  Once we fix the output of the
# # #  normal cookiecutter this won't be needed likely
# class NukikataPromptOperator(BaseOperator):
#     """Operator for nukikata type prompts."""
#
#     type = 'nukikata_prompt'
#
#     def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
#         """Initialize operator."""
#         super(NukikataPromptOperator, self).__init__(
#             operator_dict=operator_dict,
#             context=context,
#             no_input=no_input,
#             context_key=context_key,
#         )
#
#     def execute(self):
#         """Run the operator."""
#         context = {self.context_key: {}}
#         if 'context_file' in self.operator_dict:
#             context[self.context_key] = cc.utils.read_config_file(
#                 self.operator_dict['template']
#             )
#         else:
#             context[self.context_key] = self.operator_dict['context']
#
#         return cc.prompt.prompt_for_config(
#             context=context,
#             no_input=self.operator_dict['no_input']
#             if 'no_input' in self.operator_dict
#             else False,
#             context_key=self.operator_dict['context_key']
#             if 'context_key' in self.operator_dict
#             else None,
#         )