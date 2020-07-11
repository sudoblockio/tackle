# # -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os

from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class PathExistsListOperator(BaseOperator):
    """Operator for os package 'path_exists' operator.

    :param path: The path to file or directory
    :return boolean:
    """

    type = 'path_exists'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize PyInquirer operator."""
        super(PathExistsListOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )

    def execute(self):
        """Run the prompt."""
        return os.path.exists(self.operator_dict['path'])


class PathIsdirListOperator(BaseOperator):
    """
    Operator for os package 'path_exists' operator.

    :param path: The path to file or directory
    :return boolean:
    """

    type = 'path_isdir'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize PyInquirer operator."""
        super(PathIsdirListOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )

    def execute(self):
        """Run the prompt."""
        return os.path.isdir(self.operator_dict['path'])
