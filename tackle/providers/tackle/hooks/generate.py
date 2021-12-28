"""Generate hook."""
import os.path
from typing import Union, Any
from pydantic import Field
from pathlib import Path
from jinja2 import FileSystemLoader

from tackle.models import BaseHook
from tackle.render.environment import StrictEnvironment


class GenerateHook(BaseHook):
    """
    Hook for generating project outputs. Recursively renders all files and folders in a given project directory.

    - If templates is string
      - If templates is file
        - If output endswith `/`
            - Output is
      - If templates is dir
        -

    """

    type: str = 'generate'
    templates: Union[str, list] = Field(
        ...,
        description="Path to a templatable directory or file to recursively render the contents.",
    )
    output: str = Field('.', description="Path to put the output file(s).")
    copy_only: Union[str, list] = None
    overwrite_if_exists: bool = Field(
        False, description="Overwrite the output if exists."
    )
    skip_if_file_exists: bool = Field(
        False, description="Skip creating if path exists."
    )

    base_dir: Path = None
    env: Any = None
    file_system_loader: Any = None

    _args = ['templates', 'output']
    _render_exclude = ['templates']

    def execute(self):
        self.env = StrictEnvironment(context=self.input_dict)
        self.env.loader = FileSystemLoader('.')

        if isinstance(self.templates, str):
            self.generate_target(self.templates)
        elif isinstance(self.templates, list):
            for target in self.templates:
                self.generate_target(target)

    def generate_target(self, target: str):
        """

        :param target:
        :return:
        """
        # Update the input to default to searching in `templates` directory
        if os.path.exists(os.path.join("templates", target)):
            self.base_dir = Path("templates")
        else:
            self.base_dir = Path(target).parent.absolute()

        target_path = os.path.join(self.base_dir, os.path.basename(target))

        # Expand the target path
        self.output = os.path.expanduser(os.path.expandvars(self.output))
        if self.output == '.':
            self.output = os.path.basename(target)

        if os.path.isfile(target_path):
            self.generate_file(target_path, self.output)

        if os.path.isdir(target_path):
            self.generate_dir(target_path, self.output)

    def generate_file(self, input_file: str, output_path: str):
        """
        Take a target input_file and render it's contents to an output path.

        :param input_file:
        :param output_path:
        :return:
        """
        file_contents_template = self.env.get_template(input_file)
        rendered_contents = file_contents_template.render(self.output_dict)

        if output_path.endswith('/'):
            output_path = os.path.join(output_path, os.path.basename(input_file))

        file_name_template = self.env.from_string(str(output_path))
        output_path = file_name_template.render(self.output_dict)

        parent_dir = Path(output_path).parent.absolute()
        Path(parent_dir).mkdir(parents=True, exist_ok=True)

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
