"""Jinja hook."""
from jinja2.exceptions import UndefinedError
from jinja2 import FileSystemLoader

from typing import Union

from tackle import BaseHook, Field
from tackle.exceptions import UndefinedVariableInTemplate
from tackle.render.environment import StrictEnvironment
from tackle.utils.dicts import get_readable_key_path


class JinjaHook(BaseHook):
    """
    Hook for jinja templates. If given an `output`, the rendered contents are output to
     a file, otherwise the rendered contents are output as a string.
    """

    hook_type: str = 'jinja'
    # fmt: off
    template: str = Field(..., description="Path to the template to render relative to `file_system_loader`.")
    output: str = Field(None, description="Path to the output the template.")
    extra_context: dict = Field(None, description="Extra context update the global context to render with.")
    render_context: dict = Field(
        None, description="A render context that invalidates the default context."
    )
    additional_context: dict = Field(
        None, description="A map to use as additional context when rendering."
    )
    file_system_loader: Union[str, list] = Field(
        '.',
        description="List of paths or string path to directory with templates to load "
                    "from. [Docs](https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.FileSystemLoader).")
    # fmt: on

    _args: list = ['template', 'output']

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

    def execute(self) -> str:
        env = StrictEnvironment(context=self.input_dict)
        env.loader = FileSystemLoader(self.file_system_loader)
        template = env.get_template(self.template)

        jinja_context = self.render_context

        if self.extra_context:
            jinja_context.update(self.extra_context)

        try:
            # output_from_parsed_template = template.render(
            #     **{self.context_key: jinja_context}, **jinja_context
            # )
            output_from_parsed_template = template.render(**jinja_context)

        except UndefinedError as err:
            msg = f"The Jinja hook for '{get_readable_key_path(self.key_path)}' key path failed to render"
            raise UndefinedVariableInTemplate(msg, err, self.output_dict)

        if self.output is not None:
            with open(self.output, 'w') as fh:
                fh.write(output_from_parsed_template)
            return self.output
        else:
            return output_from_parsed_template
