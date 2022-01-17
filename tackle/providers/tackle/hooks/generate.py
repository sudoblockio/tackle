"""Generate hook."""
import os.path
import fnmatch
from typing import Union, Any
from pydantic import Field
from pathlib import Path
from jinja2 import FileSystemLoader
from jinja2.exceptions import UndefinedError, TemplateNotFound
import shutil

from tackle.models import BaseHook
from tackle.render.environment import StrictEnvironment
from tackle.exceptions import UndefinedVariableInTemplate


class GenerateHook(BaseHook):
    """
    Hook for generating project outputs. Recursively renders all files and folders in a
    given target directory to an output. If there is a "templates" directory and a file
    or directory that matches the `templates` input param, use that as target.
    """

    hook_type: str = 'generate'
    templates: Union[str, list] = Field(
        ...,
        description="Path or list of paths to a templatable directory or file to "
        "recursively render the contents.",
    )
    output: str = Field('.', description="Path to put the output file(s).")
    copy_without_render: Union[str, list] = []
    overwrite_if_exists: bool = Field(
        False, description="Overwrite the output if exists."
    )
    skip_if_file_exists: bool = Field(
        False, description="Skip creating if path exists."
    )
    render_context: dict = Field(
        None, description="A render context that invalidates the default context."
    )
    additional_context: Union[str, dict, list] = Field(
        None,
        description="A map to use as additional context when rendering.",
        render_by_default=True,
    )

    base_dir: Path = None
    env_: Any = None
    file_system_loader_: Any = None
    file_path_separator_: str = None  # / for mac / linux - \ for win

    _args = ['templates', 'output']

    def __init__(self, **data: Any):
        super().__init__(**data)
        if isinstance(self.copy_without_render, str):
            self.copy_without_render = [self.copy_without_render]

        self.output = os.path.expanduser(os.path.expandvars(self.output))
        if 'nt' in os.name:
            self.file_path_separator_ = '\\'
            if not self.output.startswith('\\'):
                self.output = os.path.join(self.calling_directory, self.output)
        else:
            self.file_path_separator_ = '/'
            if not self.output.startswith('/'):
                self.output = os.path.join(self.calling_directory, self.output)

        # Update the render_context that will be used
        if self.render_context is not None:
            pass
        elif self.additional_context is not None:
            if isinstance(self.additional_context, list):
                self.render_context = {
                    **self.output_dict,
                    **self.existing_context,
                }
                for i in self.additional_context:
                    self.render_context.update(i)
            else:
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

    def execute(self):
        """Generate files / directories."""
        self.env_ = StrictEnvironment(context=self.render_context)
        # https://stackoverflow.com/questions/42368678/jinja-environment-is-not-supporting-absolute-paths
        # Need to add root to support absolute paths
        self.env_.loader = FileSystemLoader(['.', '/'])

        if isinstance(self.templates, str):
            self.generate_target(self.templates)
        elif isinstance(self.templates, list):
            for target in self.templates:
                self.generate_target(target)

    def generate_target(self, target: str):
        """
        Generate from an unknown target. If there is a `templates` directory in the
        provider, check if the target matches and use that otherwise search for target.
        Generates files or directories from there.

        :param target: A generic target to generate from, file or directory.
        """
        # Update the input to default to searching in `templates` directory
        if os.path.exists(target):
            self.base_dir = Path(".")
        elif os.path.exists(os.path.join("templates", target)):
            self.base_dir = Path("templates")
        else:
            self.base_dir = Path(target).parent.absolute()

        target_path = os.path.join(self.base_dir, target)

        # Expand the target path
        self.output = os.path.expanduser(os.path.expandvars(self.output))
        if self.output == '.':
            self.output = os.path.basename(target)

        if os.path.isfile(target_path):
            self.generate_file(target_path, self.output)

        elif os.path.isdir(target_path):
            self.generate_dir(target_path, self.output)
        else:
            raise TemplateNotFound(f"Could not find {target_path}.")

    def generate_file(self, input_file: str, output_path: str):
        """
        Take a target input_file and render it's contents / file name to an output path.

        :param input_file: Input file to generate from
        :param output_path: Output file to generate to
        """
        if output_path.endswith(self.file_path_separator_):
            output_path = os.path.join(output_path, os.path.basename(input_file))

        # Render the path right away as templating mangles things later - also logical
        # to render file names.  Who wants to generate files with templates in the name?
        file_name_template = self.env_.from_string(str(output_path))
        output_path = file_name_template.render(self.render_context)

        # Make the parent directories by default
        parent_dir = Path(output_path).parent.absolute()
        Path(parent_dir).mkdir(parents=True, exist_ok=True)

        # Evaluate if it is a copy without render
        if self.is_copy_only_path(input_file):
            shutil.copyfile(input_file, output_path)
            return

        try:
            file_contents_template = self.env_.get_template(os.path.abspath(input_file))
        except UnicodeDecodeError:
            # Catch binary files with this hack and copy them over
            # TODO: Perhaps improve? In cookiecutter they used a package binary-or-not
            # or something like that but we are staying lean on dependencies in this
            # project.
            shutil.copyfile(input_file, output_path)
            return

        try:
            rendered_contents = file_contents_template.render(self.render_context)
        except UndefinedError as e:
            raise UndefinedVariableInTemplate(
                message=f"Error rendering {input_file}, {e.args[0]}.",
                error=e,
                context=self.render_context,
            )

        # Write contents
        with open(output_path, 'w') as f:
            f.write(rendered_contents)

    def generate_dir(self, input_directory: str, output_path: str):

        for i in os.listdir(input_directory):
            input = os.path.join(input_directory, i)
            output = os.path.join(output_path, i)
            if os.path.isdir(input):
                # Path(output).mkdir(parents=True, exist_ok=True)
                self.generate_dir(input, output)

            if os.path.isfile(input):
                self.generate_file(input, output)

    def is_copy_only_path(self, path):
        """Check whether the given `path` should only be copied and not rendered.

        Returns True if `path` matches a pattern in the given `context` dict,
        otherwise False.

        :param path: A file-system path referring to a file or dir that
            should be rendered or just copied.
        """
        if self.copy_without_render is None:
            return False

        for dont_render in self.copy_without_render:
            if fnmatch.fnmatch(path, dont_render):
                return True
            # TODO: Make this more logical - cookiecutter allowed without `./`
            if fnmatch.fnmatch(path, f'.{self.file_path_separator_}' + dont_render):
                return True
        return False
