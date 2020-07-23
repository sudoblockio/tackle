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
    :return: String path to the output file
    """

    type = 'jinja'

    def __init__(self, *args, **kwargs):  # noqa
        super(JinjaOperator, self).__init__(*args, **kwargs)
        self.file_system_loader = (
            self.operator_dict['file_system_loader']
            if 'file_system_loader' in self.operator_dict
            else '.'
        )

    def _execute(self):
        env = StrictEnvironment(context=self.context)

        env.loader = FileSystemLoader(self.file_system_loader)
        template = env.get_template(self.operator_dict['template_path'])

        jinja_context = (
            self.operator_dict['context'] if 'context' in self.operator_dict else {}
        )

        if 'extra_context' in self.operator_dict:
            jinja_context.update(self.operator_dict['extra_context'])

        output_from_parsed_template = template.render(
            **{self.context_key: jinja_context}
        )

        with open(self.operator_dict['output_path'], 'w') as fh:
            fh.write(output_from_parsed_template)

        return self.operator_dict['output_path']
