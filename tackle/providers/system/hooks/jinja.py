"""Jinja hook."""
from jinja2.exceptions import UndefinedError
from jinja2 import FileSystemLoader

import logging
from typing import Union

from tackle import BaseHook, Field
from tackle.exceptions import UndefinedVariableInTemplate
from tackle.render.environment import StrictEnvironment

logger = logging.getLogger(__name__)


class JinjaHook(BaseHook):
    """Hook for jinja templates. Returns string path to the output file."""

    hook_type: str = 'jinja'
    file_system_loader: str = Field('.', description="")
    template_path: str = Field(..., description="Path to the template to render")
    output_path: str = Field(..., description="Path to the output file")
    context: Union[dict, str] = Field(None, description="")
    extra_context: dict = Field({}, description="A dict to use to render")
    render_context: dict = Field(
        None, description="A render context that invalidates the default context."
    )
    additional_context: dict = Field(
        None, description="A map to use as additional context when rendering."
    )

    _args: list = ['template_path', 'output_path']

    def __init__(self, **data):
        super().__init__(**data)
        if self.render_context is not None:
            pass
        elif self.additional_context is not None:
            self.render_context = {
                **self.output_dict,
                **self.additional_context,
                **self.existing_context,
            }
        else:
            self.render_context = {
                **self.output_dict,
                **self.existing_context,
            }

    def execute(self) -> dict:
        env = StrictEnvironment(context=self.input_dict)
        env.loader = FileSystemLoader(self.file_system_loader)
        template = env.get_template(self.template_path)

        jinja_context = self.output_dict.copy()

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
