# -*- coding: utf-8 -*-

"""Jinja hook."""
from __future__ import unicode_literals
from __future__ import print_function

from jinja2.exceptions import UndefinedError
from jinja2 import FileSystemLoader

import logging
from typing import Dict, Union

from tackle import BaseHook, Field
from tackle.exceptions import UndefinedVariableInTemplate
from tackle.render.environment import StrictEnvironment

logger = logging.getLogger(__name__)


class JinjaHook(BaseHook):
    """
    Hook for jinja templates. Returns string path to the output file.
    """

    type: str = 'jinja'
    file_system_loader: str = Field('.', description="")
    template_path: str = Field(..., description="Path to the template to render")
    output_path: str = Field(..., description="Path to the output file")
    context: Union[dict, str] = Field(None, description="")
    extra_context: dict = Field({}, description="A dict to use to render")

    _args: list = ['template_path', 'output_path']

    def execute(self) -> dict:
        env = StrictEnvironment(context=self.input_dict)
        env.loader = FileSystemLoader(self.file_system_loader)
        template = env.get_template(self.template_path)

        jinja_context = dict(self.output_dict)

        if self.extra_context:
            jinja_context.update(self.extra_context)

        try:
            # output_from_parsed_template = template.render(
            #     **{self.context_key: jinja_context}, **jinja_context
            # )
            output_from_parsed_template = template.render(**jinja_context)

        except UndefinedError as err:
            msg = f"The Jinja hook for '{self.key}' failed to render"
            raise UndefinedVariableInTemplate(msg, err, self.output_dict)

        with open(self.output_path, 'w') as fh:
            fh.write(output_from_parsed_template)

        return self.output_path
