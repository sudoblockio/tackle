# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

from jinja2 import FileSystemLoader
import logging

from cookiecutter.operators import BaseOperator
from cookiecutter.environment import StrictEnvironment

logger = logging.getLogger(__name__)


class JinjaOperator(BaseOperator):
    """Operator for jinja templates."""

    type = 'jinja'

    def __init__(self, operator_dict, context=None, no_input=False):
        """Initialize operator."""  # noqa
        super(JinjaOperator, self).__init__(
            operator_dict=operator_dict, context=context, no_input=no_input
        )
        self.post_gen_operator = True

    def execute(self):
        """Run the operator."""  # noqa
        env = StrictEnvironment(context=self.context)
        env.loader = FileSystemLoader('.')
        template = env.get_template(self.operator_dict['template_path'])

        output_from_parsed_template = template.render(**self.context)
        with open(self.operator_dict['output_path'], 'w') as fh:
            fh.write(output_from_parsed_template)

        return self.operator_dict['output_path']
