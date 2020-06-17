# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import sys
import logging

from cookiecutter.operators import BaseOperator
import subprocess

logger = logging.getLogger(__name__)


class CommandOperator(BaseOperator):
    """Operator for PyInquirer type prompts."""

    type = 'command'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize `command` Hook."""  # noqa
        super(CommandOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )
        # Defaulting to run inline
        self.post_gen_operator = (
            self.operator_dict['delay'] if 'delay' in self.operator_dict else False
        )

    def execute(self):
        """Run the operator."""  # noqa
        p = subprocess.Popen(
            self.operator_dict['command'],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, err = p.communicate()

        if err:
            sys.exit(err)

        return output.decode("utf-8")


# TODO: We need a way to spawn a pseudo terminal like session.
#  This should likely be the default for this operator
#
# class CommandInputOperator(BaseOperator):
#     """Operator for PyInquirer type prompts."""
#
#     type = 'command_input'
#
#     def __init__(self, operator_dict, context=None):
#         """Initialize PyInquirer Hook."""  # noqa
#         super(CommandInputOperator, self).__init__(
#             operator_dict=operator_dict, context=context
#         )
#         self.post_gen_operator = True
#
#     def execute(self):
#         """Run the operator."""  # noqa
#         p = subprocess.Popen(
#             self.operator_dict['command'],
#             shell=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#         )
#         output, err = p.communicate()
#
#         if err:
#             sys.exit(err)
#
#         return output.decode("utf-8")
