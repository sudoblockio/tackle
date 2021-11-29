"""Generate hook."""
import logging
from pydantic import Field

from tackle.models import BaseHook, Context
from tackle.generate import generate_files

logger = logging.getLogger(__name__)


# TODO: WIP - May not need but would be nice to call the generate
#  function from a hook
class GenerateHook(BaseHook):
    """
    Hook for generating project outputs. Recursively renders all files and folders in a given project directory.
    """

    type: str = 'generate'
    project_dir: str = Field(
        '.',
        description="Directory with a templatable directory to recursively render the contents.",
    )
    output_dir: str = Field('.', description="Directory to put the output files.")
    overwrite_if_exists: bool = Field(
        False, description="Overwrite the output if exists."
    )
    skip_if_file_exists: bool = Field(
        False, description="Skip creating if path exists."
    )
    accept_hooks: bool = Field(
        True, description="Boolean for whether to accept pre/post gen project gooks."
    )

    def execute(self):
        context = Context(
            input_dict=self.input_dict,
            output_dict=self.output_dict,
            context_key=self.context_key,
            tackle_gen='tackle',
            repo_dir=self.project_dir,
            output_dir=self.output_dir,
            overwrite_if_exists=self.overwrite_if_exists,
            skip_if_file_exists=self.skip_if_file_exists,
            accept_hooks=self.accept_hooks,
        )

        generate_files(context=context)
