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
    """
    Operator for jinja templates.

    :param template_path: Path to the template to render
    :param extra_context: A dict to use to render
    :param output_path: Path to the output file
    :return String path to the output file
    """

    type = 'jinja'

    def __init__(self, operator_dict, context=None, context_key=None, no_input=False):
        """Initialize operator."""
        super(JinjaOperator, self).__init__(
            operator_dict=operator_dict,
            context=context,
            no_input=no_input,
            context_key=context_key,
        )
        # Defaulting to run inline
        self.post_gen_operator = (
            self.operator_dict['delay'] if 'delay' in self.operator_dict else False
        )
        self.file_system_loader = (
            self.operator_dict['file_system_loader']
            if 'file_system_loader' in self.operator_dict
            else '.'
        )

    def execute(self):
        """Run the operator."""
        env = StrictEnvironment(context=self.context)

        env.loader = FileSystemLoader(self.file_system_loader)
        template = env.get_template(self.operator_dict['template_path'])

        extra_context = (
            self.operator_dict['extra_context']
            if 'extra_context' in self.operator_dict
            else {}
        )
        self.context.update({self.context_key: extra_context})
        output_from_parsed_template = template.render(**self.context)
        with open(self.operator_dict['output_path'], 'w') as fh:
            fh.write(output_from_parsed_template)

        return self.operator_dict['output_path']
