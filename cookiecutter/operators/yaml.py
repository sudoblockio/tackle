# -*- coding: utf-8 -*-

"""Functions for generating a project from a project template."""
from __future__ import unicode_literals
from __future__ import print_function

import logging
import yaml
from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)


class YamlOperator(BaseOperator):
    """Operator for yaml type prompts."""

    type = 'yaml'

    def __init__(self, operator_dict, context=None):
        """Initialize yaml operator."""  # noqa
        super(YamlOperator, self).__init__(operator_dict=operator_dict, context=context)
        self.post_gen_operator = True

    def execute(self):
        """Run the operator."""  # noqa
        if 'contents' in self.operator_dict:
            with open(self.operator_dict['path'], 'w') as f:
                yaml.dump(self.operator_dict['contents'], f)

        else:
            with open(self.operator_dict['path'], 'w') as f:
                return yaml.load(f)
