import copy
from typing import Any, Union

from pydantic import SecretStr

import tackle as tkl
from tackle import BaseHook, Context, Field


class TackleHook(BaseHook):
    """Hook for calling external tackle providers."""

    hook_name = 'tackle'

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
    no_input: bool = Field(
        None,
        description="A boolean for if you want to suppress prompt inputs."
    )
    latest: bool = Field(
        False,
        description="For remote providers, use the latest commit."
    )
    context_file: str = Field(
        None,
        description="The file to run inside a repo input.",
    )
    extra_context: dict = Field(
        None,
        description="Any additional context to use when calling the hook. Like "
                    "existing context."
    )
    password: SecretStr = Field(
        None,
        description="A password to use for repo inputs.",
    )
    directory: str = Field(
        None,
        description="The directory to run inside for repo inputs."
    )
    find_in_parent: bool = Field(
        False,
        description="Search for target in parent directory. Only relevant for local "
                    "targets.",
    )
    override: dict = Field(
        {},
        description="A dictionary of keys to override.",
    )
    additional_args: Union[list, Any] = Field(
        [],
        description="Arguments to pass on either directly as a string or as a list of "
                    "strings."
    )
    # fmt: on

    args: list = ['input_arg', 'additional_args']
    kwargs: str = 'override'
    _docs_order = 0

    def exec(self, context: Context) -> dict | list:
        if self.input_arg is None:
            # If not given, assume we're looking for default tackle file in current dir
            self.input_arg = '.'

        existing_context = {}

        if self.override != {}:
            # This is a hack as we need extra vars to be mapped to both the
            # existing_context (allowing rendering of unknown vars) and the overrides
            # (allowing for calling of declarative hooks with args / kwargs)
            existing_context.update(self.override)

        if context.data.existing:
            existing_context.update(context.data.existing)

        if context.data.temporary:
            existing_context.update(context.data.temporary)

        # if self.private_context:
        #     existing_context.update(self.private_context)

        if context.data.public:
            existing_context.update(context.data.public)

        if self.extra_context:
            existing_context.update(self.extra_context)

        if isinstance(self.additional_args, str):
            self.additional_args = [self.additional_args]

        pass

        output_context = tkl.main.tackle(
            *(self.input_arg, *self.additional_args),
            checkout=self.checkout,
            latest=self.latest,
            directory=self.directory,
            find_in_parent=self.find_in_parent,
            no_input=self.no_input if not self.no_input else context.no_input,
            verbose=context.verbose,
            overrides=self.override,
            existing_data=existing_context,
            # Evaluated in factory
            _paths=context.path,
            # TODO: Handle this in factory? Don't want to copy every time?
            _data=copy.deepcopy(context.data),
            # Implicit
            # _hooks=context.hooks,
            **self.override,
        )

        return output_context
