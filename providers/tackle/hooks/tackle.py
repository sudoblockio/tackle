from pydantic import SecretStr
from typing import Union

import tackle as tkl
from tackle import BaseHook, Field


class TackleHook(BaseHook):
    """Hook for calling external tackle providers."""

    hook_name: str = 'tackle'

    # fmt: off
    input_arg: str = Field(
        None,
        description="The input can be one of repo, file path, directory with "
                    "tackle.yaml, zip file, or if left blank parent tackle file."
    )
    checkout: str = Field(
        None,
        description="The branch or version to checkout for repo type inputs_strings."
    )
    latest: bool = Field(
        False,
        description="For remote providers, use the latest commit."
    )
    context_file: str = Field(None, description="The file to run inside a repo input.")
    extra_context: dict = Field(
        None,
        description="Any additional context to use when calling the hook. Like existing context.")
    # context: dict = Field(
    #     None,
    #     description="A context to use that overrides the current context."
    # )
    password: SecretStr = Field(None, description="A password to use for repo inputs.")
    directory: str = Field(
        None,
        description="The directory to run inside for repo inputs."
    )
    find_in_parent: bool = Field(
        False,
        description="Search for target in parent directory. Only relevant for local "
                    "targets.")

    override: dict = Field({}, description="A dictionary of keys to override.")

    additional_args: Union[list, str] = Field(
        None,
        description="Arguments to pass on either directly as a string or as a list of "
                    "strings."
    )
    # fmt: on

    args: list = ['input_arg', 'additional_args']
    kwargs: str = 'override'
    _docs_order = 0

    def exec(self) -> dict:
        if self.input_arg is None:
            # If not given, assume we're looking for default tackle file in current dir
            self.input_arg = '.'

        existing_context = {}

        if self.override != {}:
            # This is a hack as we need extra vars to be mapped to both the
            # existing_context (allowing rendering of unknown vars) and the overrides
            # (allowing for calling of declarative hooks with args / kwargs)
            existing_context.update(self.override)

        if self.context.data.existing:
            existing_context.update(self.context.data.existing)

        if self.context.data.temporary:
            existing_context.update(self.context.data.temporary)

        # if self.private_context:
        #     existing_context.update(self.private_context)

        if self.context.data.public:
            existing_context.update(self.context.data.public)

        if self.extra_context:
            existing_context.update(self.extra_context)

        if isinstance(self.additional_args, str):
            self.additional_args = [self.additional_args]

        output_context = tkl.main.tackle(
            self.input_arg,
            checkout=self.checkout,
            latest=self.latest,
            directory=self.directory,
            no_input=self.no_input,
            find_in_parent=self.find_in_parent,
            verbose=self.context.verbose,
            overrides=self.override,
            existing_data=existing_context,
            # Evaluated
            # existing_context=existing_context,
            _paths=self.context.path,
            _data=self.context.data.__copy__(),
            # Implicit
            _hooks=self.context.hooks,
        )


        return output_context
