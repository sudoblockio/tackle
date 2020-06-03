# -*- coding: utf-8 -*-

"""Functions for generating a project from a project template."""
from __future__ import unicode_literals
from __future__ import print_function

from jinja2 import FileSystemLoader
import logging

from cookiecutter.operators import BaseOperator
from cookiecutter.environment import StrictEnvironment

logger = logging.getLogger(__name__)


class JinjaOperator(BaseOperator):
    """Operator for calling external cookiecutters."""

    type = 'jinja'

    def __init__(self, operator_dict, context):
        """Initialize PyInquirer Hook."""  # noqa
        super(JinjaOperator, self).__init__(
            operator_dict=operator_dict, context=context
        )
        self.post_gen_operator = True

    def execute(self):
        """Run the prompt."""  # noqa
        env = StrictEnvironment(context=self.context)
        env.loader = FileSystemLoader('.')
        template = env.get_template(self.operator_dict['template_path'])

        output_from_parsed_template = template.render(**self.context)
        with open(self.operator_dict['output_path'], 'w') as fh:
            fh.write(output_from_parsed_template)