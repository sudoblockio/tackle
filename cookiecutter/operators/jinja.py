# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

from jinja2 import FileSystemLoader
import logging
from typing import Dict

# from pathlib import Path

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

    type: str = 'jinja'
    file_system_loader: str = '.'
    template_path: str
    output_path: str
    context: Dict = {}
    extra_context: Dict = None

    def execute(self):
        env = StrictEnvironment(context=self.context)

        env.loader = FileSystemLoader(self.file_system_loader)
        template = env.get_template(self.template_path)

        jinja_context = self.context

        if self.extra_context:
            jinja_context.update(self.extra_context)

        output_from_parsed_template = template.render(
            **{self.context_key: jinja_context}
        )

        with open(self.output_path, 'w') as fh:
            fh.write(output_from_parsed_template)

        return self.output_path
