"""Environment variable hooks."""
import os
import logging
import platform

from tackle.models import BaseHook, Field

logger = logging.getLogger(__name__)


class GetEnvHook(BaseHook):
    """Hook for getting environment variables."""

    type: str = 'get_env'
    environment_variable: str = Field(
        None,
        description="Dict for setting and string for getting environment variables",
    )
    fallback: str = Field(None, description="A fallback for getting.")

    _args: list = ['environment_variable', 'fallback']

    def execute(self):
        """Set env vars."""
        if platform.system() == 'Windows':
            from tackle.exceptions import ContributionNeededException

            raise ContributionNeededException()
            # robcxyz - Not working on windows support but would love PRs
        else:
            return os.getenv(self.environment_variable, self.fallback)


class EnvironmentVariableHook(BaseHook):
    """Hook for setting environment variables."""

    type: str = 'set_env'
    environment_variable: str = Field(
        ..., description="The name of the environment variable to set."
    )
    value: str = Field(None, description="The value to set it.")

    _args: list = ['environment_variable', 'value']

    def execute(self):
        """Get or set env vars."""
        if platform.system() == 'Windows':
            from tackle.exceptions import ContributionNeededException

            raise ContributionNeededException()
            # robcxyz - Not working on windows support but would love PRs
        else:
            # TODO: Implement parsing for strings to set -> export THING=stuff
            os.environ[self.environment_variable] = self.value
            return self.value


class ExportHook(BaseHook):
    """
    Hook for setting environment variables that returns None

    Sets with input dict. Gets with input string.

    :param input: Dict for setting and string for getting environment variables
    :param fallback: A fallback for getting.
    :return: input
    """

    type: str = 'export'
    environment_variable: str = Field(
        ..., description="The name of the environment variable to set."
    )
    value: str = Field(None, description="The value to set it.")

    _args: list = ['environment_variable', 'value']

    # TODO: Implement parsing for strings to set -> <: export THING=stuff
    def execute(self):
        """Set env vars."""
        if platform.system() == 'Windows':
            from tackle.exceptions import ContributionNeededException

            raise ContributionNeededException()
            # robcxyz - Not working on windows support but would love PRs
        else:
            os.environ[self.environment_variable] = self.value
        return


class UnsetHook(BaseHook):
    """Hook for unsetting environment variables."""

    type: str = 'unset'
    environment_variable: str = Field(
        ..., description="The name of the environment variable to set."
    )

    _args: list = ['environment_variable']

    def execute(self):
        """Set env vars."""
        if platform.system() == 'Windows':
            from tackle.exceptions import ContributionNeededException

            raise ContributionNeededException()
            # robcxyz - Not working on windows support but would love PRs
        else:
            os.unsetenv(self.environment_variable)
        return
