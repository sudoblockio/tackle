"""Tackle hooks."""
import tackle as tkl
from pydantic import SecretStr

from tackle.models import BaseHook, Field


class TackleHook(BaseHook):
    """
    Hook  for calling external tackle.

    :param template: A directory containing a project template,
        or a URL to a git repository.
    :param templates: A list of directories containing a project template,
        or a URL to a git repository.
    :param checkout: The branch, tag or commit ID to checkout after clone.
    :param no_input: Prompt the user at command line for manual configuration?
    :param override_inputs: A dictionary of context that overrides default
        and user configuration.
    :param existing_context: An additional dictionary to use in rendering
        additional prompts.
    :param replay: Do not prompt for input, instead read from saved json. If
        ``True`` read from the ``replay_dir``.
        if it exists
    :param output_dir: Where to output the generated project dir into.
    :param config_file: User configuration file path.
    :param default_config: Use default values rather than a config file.
    :param password: The password to use when extracting the repository.
    :param directory: Relative path to a tackle box / cookiecutter template
        in a repository.
    :param accept_hooks: Accept pre and post hooks if set to `True`.

    :return: Dictionary of output
    """

    hook_type: str = 'tackle'

    # fmt: off

    input_string: str = Field(
        None, description="The input can be one of repo, file path, directory with tackle.yaml, zip file, or if left blank parent tackle file.")
    checkout: str = Field(None, description="The branch or version to checkout for repo type inputs_strings.")
    context_file: str = Field(None, description="The file to run inside a repo input.")
    additional_context: dict = Field(
        None, description="Any additional context to use when calling the hook. Like existing context.")
    context: dict = Field(None, description="A context to use that overrides the current context.")
    password: SecretStr = Field(None, description="A password to use for repo inputs.")
    directory: str = Field(None, description="The directory to run inside for repo inputs.")

    # fmt: on

    _args = ['input_string']

    def execute(self):

        # if self.existing_context in (None, {}):
        #     existing_context = self.output_dict
        # else:
        #     existing_context = self.existing_context

        if self.context:
            existing_context = self.context
        else:
            existing_context = self.output_dict.copy()
            existing_context.update(self.existing_context)

            if self.additional_context:
                existing_context.update(self.additional_context)

        output_context = tkl.main.tackle(
            self.input_string,
            checkout=self.checkout,
            password=self.password,
            directory=self.directory,
            calling_directory=self.calling_directory,
            # Evaluated
            existing_context=existing_context,
            # Implicit
            providers=self.providers_,
            no_input=self.no_input,
        )

        return dict(output_context)
