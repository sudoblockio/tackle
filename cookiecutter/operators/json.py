# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import json
from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class JsonOperator(BaseOperator):
    """Operator for json."""

    type = 'json'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize json operator."""  # noqa
        super(JsonOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )
        # Defaulting to run inline
        self.post_gen_operator = (
            self.operator_dict['delay'] if 'delay' in self.operator_dict else False
        )

    def execute(self):
        """Run the operator."""  # noqa
        if 'contents' in self.operator_dict:
            with open(self.operator_dict['path'], 'w') as f:
                json.dump(self.operator_dict['contents'], f)
            return self.operator_dict['path']

        else:
            with open(self.operator_dict['path'], 'r') as f:
                return json.load(f)
