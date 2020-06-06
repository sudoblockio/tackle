# -*- coding: utf-8 -*-

"""Functions for generating a project from a project template."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import json
from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class JsonOperator(BaseOperator):
    """Operator for yaml type prompts."""

    type = 'json'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize yaml Hook."""  # noqa
        super(JsonOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )
        self.post_gen_operator = True

    def execute(self):
        """Run the operator."""  # noqa
        if 'contents' in self.operator_dict:
            with open(self.operator_dict['path'], 'w') as f:
                json.dump(self.operator_dict['contents'], f)

        else:
            with open(self.operator_dict['path'], 'w') as f:
                return json.load(f)
