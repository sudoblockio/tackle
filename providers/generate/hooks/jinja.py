from typing import Union

from jinja2 import FileSystemLoader
from jinja2.exceptions import UndefinedError

from providers.generate.hooks.common import init_context
from providers.generate.hooks.exceptions import UndefinedVariableInTemplate
from tackle import BaseHook, Context, Field


class JinjaHook(BaseHook):
    """
    Hook for jinja templates. If given an `output`, the rendered contents are output to
     a file, otherwise the rendered contents are output as a string.
    """

    hook_name = 'jinja'
    # fmt: off
    template: str = Field(
        ...,
        description="Path to the template to render relative to `file_system_loader`.")
    output: str = Field(
        None,
        description="Path to the output the template.")
    extra_context: dict = Field(
        None,
        description="Extra context update the global context to render with.")
    render_context: dict = Field(
        None,
        description="A render context that invalidates the default context."
    )
    additional_context: dict = Field(
        None,
        description="A map to use as additional context when rendering."
    )
    file_system_loader: Union[str, list] = Field(
        '.',
        description="List of paths or string path to directory with templates to load "
                    "from. [Docs](https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.FileSystemLoader).")
    # fmt: on

    args: list = ['template', 'output']

    # def _init_context(self, context: 'Context'):
    #     # Update the render_context that will be used
    #     if self.render_context is not None:
    #         return
    #
    #     # fmt: off
    #     existing = context.data.existing if context.data.existing is not None else {}
    #     temporary = context.data.temporary if context.data.temporary is not None else {}
    #     private = context.data.private if context.data.private is not None else {}
    #     public = context.data.public if context.data.public is not None else {}
    #     # fmt: on
    #
    #     self.render_context = {
    #         **existing,
    #         **temporary,
    #         **private,
    #         **public,
    #     }
    #
    #     if self.extra_context is not None:
    #         if isinstance(self.extra_context, list):
    #             for i in self.extra_context:
    #                 self.render_context.update(i)
    #         else:
    #             self.render_context.update(self.extra_context)

    def exec(self, context: Context) -> str:
        # self._init_context(context=context)
        init_context(self=self, context=context)
        context.env_.loader = FileSystemLoader(self.file_system_loader)
        template = context.env_.get_template(self.template)

        try:
            output_from_parsed_template = template.render(**self.render_context)
        except UndefinedError as err:
            msg = f"The `jinja` hook failed to render -> {err}"
            raise UndefinedVariableInTemplate(msg, context=context) from None

        if self.output is not None:
            with open(self.output, 'w') as fh:
                fh.write(output_from_parsed_template)
            return self.output
        else:
            return output_from_parsed_template
