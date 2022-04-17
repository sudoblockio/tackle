import tackle as tkl
from pydantic import SecretStr

from tackle.models import BaseHook, Field


class TackleHook(BaseHook):
    """Hook for calling external tackle providers."""

    hook_type: str = 'tackle'

    # fmt: off
    input_string: str = Field(
        None,
        description="The input can be one of repo, file path, directory with tackle.yaml, zip file, or if left blank parent tackle file.")
    checkout: str = Field(None,
                          description="The branch or version to checkout for repo type inputs_strings.")
    context_file: str = Field(None, description="The file to run inside a repo input.")
    extra_context: dict = Field(
        None,
        description="Any additional context to use when calling the hook. Like existing context.")
    context: dict = Field(None,
                          description="A context to use that overrides the current context.")
    password: SecretStr = Field(None, description="A password to use for repo inputs.")
    directory: str = Field(None,
                           description="The directory to run inside for repo inputs.")
    find_in_parent: bool = Field(
        False, description="Search for target in parent directory. Only relevant for "
                           "local targets.")

    override: dict = Field({}, description="A dictionary of keys to override.")
    # fmt: on

    args: list = ['input_string']
    _docs_order = 0

    def exec(self) -> dict:
        existing_context = {}

        if self.context:
            existing_context.update(self.context)

        if self.existing_context:
            existing_context.update(self.existing_context)

        if self.temporary_context:
            existing_context.update(self.temporary_context)

        if self.private_context:
            existing_context.update(self.private_context)

        if self.public_context:
            existing_context.update(self.public_context)

        if self.extra_context:
            existing_context.update(self.extra_context)

        output_context = tkl.main.tackle(
            self.input_string,
            checkout=self.checkout,
            password=self.password,
            directory=self.directory,
            calling_directory=self.calling_directory,
            calling_file=self.calling_file,
            # Evaluated
            existing_context=existing_context,
            # Implicit
            provider_hooks=self.provider_hooks,
            no_input=self.no_input,
            global_kwargs=self.override,
            find_in_parent=self.find_in_parent,
            verbose=self.verbose,
        )

        return output_context
