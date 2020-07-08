# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging

from cookiecutter.operators import BaseOperator
import cookiecutter as cc

logger = logging.getLogger(__name__)


class BlockOperator(BaseOperator):
    """Operator for printing an input and returning the output."""

    type = 'block'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize operator."""
        super(BlockOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )

    def execute(self):
        """Run the operator."""
        return cc.prompt.prompt_for_config(
            context={self.context_key: self.operator_dict['items']},
            no_input=self.no_input,
            context_key=self.context_key,
            existing_context=self.context,
        )
