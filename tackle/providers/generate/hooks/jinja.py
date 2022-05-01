from jinja2.exceptions import UndefinedError
from jinja2 import FileSystemLoader

from typing import Union

from tackle import BaseHook, Field
from tackle.providers.generate.hooks.exceptions import UndefinedVariableInTemplate


class JinjaHook(BaseHook):
    """
    Hook for jinja templates. If given an `output`, the rendered contents are output to
     a file, otherwise the rendered contents are output as a string.
    """

    hook_type: str = 'jinja'
    # fmt: off
    template: str = Field(...,
                          description="Path to the template to render relative to `file_system_loader`.")
    output: str = Field(None, description="Path to the output the template.")
    extra_context: dict = Field(None,
                                description="Extra context update the global context to render with.")
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

    args: list = ['template', 'output']

    def _init_context(self):
        # Update the render_context that will be used
        if self.render_context is not None:
            return

        # fmt: off
        existing_context = self.existing_context if self.existing_context is not None else {}
        temporary_context = self.temporary_context if self.temporary_context is not None else {}
        private_context = self.private_context if self.private_context is not None else {}
        public_context = self.public_context if self.public_context is not None else {}
        # fmt: on

        self.render_context = {
            **existing_context,
            **temporary_context,
            **private_context,
            **public_context,
        }

        if self.extra_context is not None:
            if isinstance(self.extra_context, list):
                for i in self.extra_context:
                    self.render_context.update(i)
            else:
                self.render_context.update(self.extra_context)

    def exec(self) -> str:
        self._init_context()
        self.env_.loader = FileSystemLoader(self.file_system_loader)
        template = self.env_.get_template(self.template)

        try:
            output_from_parsed_template = template.render(**self.render_context)
        except UndefinedError as err:
            msg = f"The `jinja` hook failed to render -> {err}"
            raise UndefinedVariableInTemplate(msg, hook=self) from None

        if self.output is not None:
            with open(self.output, 'w') as fh:
                fh.write(output_from_parsed_template)
            return self.output
        else:
            return output_from_parsed_template
