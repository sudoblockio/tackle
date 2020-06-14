# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import cookiecutter
import logging

from cookiecutter.operators import BaseOperator


logger = logging.getLogger(__name__)


class NukikataOperator(BaseOperator):
    """Operator for calling external cookiecutters."""

    type = 'nukikata'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize operator."""  # noqa
        super(NukikataOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )
        # Doesn't work, gets called twice
        self.post_gen_operator = (
            self.operator_dict['delay'] if 'delay' in self.operator_dict else False
        )

    def execute(self):
        """Run the operator."""  # noqa

        return cookiecutter.main.cookiecutter(
            template=self.operator_dict['template'],
            checkout=self.operator_dict['checkout']
            if 'checkout' in self.operator_dict
            else None,
            no_input=self.operator_dict['no_input']
            if 'no_input' in self.operator_dict
            else False,
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


# TODO: Is this needed?  We need to verify that the
# class NukikataPromptOperator(BaseOperator):
#     """Operator for cookiecutter type prompts."""
#
#     type = 'nukikata_prompt'
#
#     def __init__(self, operator_dict, context=None):
#         """Initialize operator."""  # noqa
#         super(NukikataPromptOperator, self).__init__(
#             operator_dict=operator_dict, context=context
#         )
#
#     def execute(self):
#         """Run the operator."""  # noqa
#         if 'template' in self.operator_dict:
#             context = cookiecutter.utils.read_config_file(
#                 self.operator_dict['template']
#             )  # noqa
#         else:
#             context = self.operator_dict['context']
#
#         return cookiecutter.prompt_for_config.cookiecutter(
#             context=context,
#             no_input=self.operator_dict['no_input']
#             if 'no_input' in self.operator_dict
#             else False,
#         )  # noqa
