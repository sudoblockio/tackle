# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
from typing import Dict

from cookiecutter.operators import BaseOperator
import cookiecutter as cc

logger = logging.getLogger(__name__)


class BlockOperator(BaseOperator):
    """
    Operator for blocks of operators.

    This is a special case where the operators input variables are not rendered
    until it is later executed.

    :param items: Map of inputs
    """

    type: str = 'block'
    items: Dict

    def execute(self):
        return cc.prompt.prompt_for_config(
            context={self.context_key: self.items},
            no_input=self.no_input,
            context_key=self.context_key,
            existing_context=self.cc_dict,
        )
