# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import yaml
from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class YamlOperator(BaseOperator):
    """Operator for yaml."""

    type = 'yaml'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize yaml operator."""  # noqa
        super(YamlOperator, self).__init__(
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
                yaml.dump(self.operator_dict['contents'], f)

        else:
            with open(self.operator_dict['path'], 'r') as f:
                return yaml.safe_load(f)
