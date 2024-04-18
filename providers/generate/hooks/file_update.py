from typing import Union

from providers.generate.hooks.common import init_context
from tackle import BaseHook, Context, Field


class FileUpdateHook(BaseHook):
    """
    Hook for jinja templates. If given an `output`, the rendered contents are output to
     a file, otherwise the rendered contents are output as a string.
    """

    hook_name = 'file_update'
    # fmt: off
    template: str = Field(..., description="Path to the template to render relative to `file_system_loader`.")

    start_marker: str = Field("<!-start->", description="Some marker in the template to start replacing the contents within.")
    end_marker: str = Field("<!-end->", description="Some marker in the template to stop replacing the contents within.")

    start_line: int = Field(None, description="The line number to update from. Supersedes marker.")

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

    args: list = ['template']

    _wip = True

    def find_line_in_template(self, file):
        start_line = None
        end_line = None

        for i, v in enumerate(file):
            if start_line is None and v.startswith(self.start_marker):
                start_line = i + 1
            if (
                start_line is not None
                and end_line is None
                and v.startswith(self.end_marker)
            ):
                end_line = i

        if end_line is None:
            end_line = len(file)

        return start_line, end_line

    def exec(self, context: 'Context'):
        init_context(self=self, context=context)

        with open(self.template) as f:
            file = f.readlines()

            if self.start_line is None:
                self.start_line, end_line = self.find_line_in_template(file)

            for i in range(self.start_line, end_line):
                file.pop(i)

            print()

        # self.env_.loader = FileSystemLoader(self.file_system_loader)
        # template = self.env_.get_template(self.template)
        #
        # try:
        #     output_from_parsed_template = template.render(**self.render_context)
        # except UndefinedError as err:
        #     msg = f"The Jinja hook for '{get_readable_key_path(self.key_path)}' key path failed to render"
        #     raise UndefinedVariableInTemplate(msg, err, self.public_context)
        #
        # if self.output is not None:
        #     with open(self.output, 'w') as fh:
        #         fh.write(output_from_parsed_template)
        #     return self.output
        # else:
        #     return output_from_parsed_template
