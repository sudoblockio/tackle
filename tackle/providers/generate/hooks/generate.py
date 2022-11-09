import os.path
import fnmatch
from typing import Union
from pydantic import Field
from pathlib import Path
from jinja2 import FileSystemLoader
from jinja2.exceptions import UndefinedError
import shutil
from typing import List

from tackle.models import BaseHook
from tackle.providers.generate.hooks.exceptions import (
    UndefinedVariableInTemplate,
    GenerateHookTemplateNotFound,
)


class GenerateHook(BaseHook, smart_union=True):
    """
    Hook for generating project outputs. Recursively renders all files and folders in a
     given target directory to an output. If there is a "templates" directory and a file
     or directory that matches the `templates` input param, use that as target.
    """

    hook_type: str = 'generate'
    # fmt: off
    templates: Union[str, list] = Field(
        "templates",
        description="Path or list of paths to a templatable directory or file to "
                    "recursively render the contents.",
    )
    output: str = Field('.', description="Path to put the output file(s).")
    copy_without_render: Union[str, list] = Field(
        [], description="List of path to files to only copy and not render."
    )
    overwrite_if_exists: bool = Field(
        False, description="Overwrite the output if exists."
    )
    skip_if_file_exists: bool = Field(
        False, description="Skip creating if path exists."
    )
    skip_overwrite_files: list = Field(
        [], description="List of files to skip generating over if they exist."
    )
    render_context: dict = Field(
        None, description="A render context that invalidates the default context."
    )
    extra_context: Union[str, dict, List[dict]] = Field(
        None,
        description="A map / list of maps to use as extra context when rendering. "
                    "Lists inputs are merged together as lists themselves don't make "
                    "sense.",
        render_by_default=True,
    )
    file_system_loader: Union[str, list] = Field(
        '.',
        description="List of paths or string path to directory with templates to load "
                    "from. [Docs](https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.FileSystemLoader)."  # noqa
    )

    base_dir_: Path = None
    # env_: Any = None
    file_path_separator_: str = None  # / for mac / linux - \ for win
    # fmt: on

    args: list = ['templates', 'output']

    def _init_paths(self):
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

    def exec(self):
        """Generate files / directories."""
        self._init_paths()
        self._init_context()

        # https://stackoverflow.com/questions/42368678/jinja-environment-is-not-supporting-absolute-paths
        # Need to add root to support absolute paths
        if isinstance(self.file_system_loader, str):
            self.env_.loader = FileSystemLoader([self.file_system_loader, '/'])
        else:
            self.env_.loader = FileSystemLoader(self.file_system_loader + ['/'])

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
            self.base_dir_ = Path(".")
        elif os.path.exists(os.path.join("templates", target)):
            self.base_dir_ = Path("templates")
        else:
            self.base_dir_ = Path(target).parent.absolute()

        target_path = os.path.join(self.base_dir_, target)

        # Expand the target path
        self.output = os.path.expanduser(os.path.expandvars(self.output))
        if self.output == '.':
            self.output = os.path.basename(target)

        if os.path.isfile(target_path):
            self.generate_file(target_path, self.output)

        elif os.path.isdir(target_path):
            self.generate_dir(target_path, self.output)
        else:
            raise GenerateHookTemplateNotFound(
                f"Could not find {target_path}.", hook=self
            ) from None

    def generate_file(self, input_file: str, output_path: str):
        """
        Take a target input_file and render its contents / file name to an output path.

        :param input_file: Input file to generate from
        :param output_path: Output file to generate to
        """
        if output_path.endswith(self.file_path_separator_):
            output_path = os.path.join(output_path, os.path.basename(input_file))

        # For skip operations -> Useful when we only want to render once
        if os.path.exists(output_path):
            if self.skip_if_file_exists:
                return

            if self.skip_overwrite_files is not None:
                for i in self.skip_overwrite_files:
                    skip_output_path = os.path.join(Path(output_path).parent, i)
                    if output_path == skip_output_path:
                        return

        # Render the path right away as templating mangles things later - also logical
        # to render file names.  Who wants to generate files with templates in the name?
        file_name_template = self.env_.from_string(str(output_path))
        try:
            output_path = file_name_template.render(self.render_context)
        except UndefinedError as e:
            msg = f"The `generate` hook failed to render -> {e}"
            raise UndefinedVariableInTemplate(msg, hook=self) from None

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
            msg = f"The `generate` hook failed to render -> {e}"
            raise UndefinedVariableInTemplate(msg, hook=self) from None

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
