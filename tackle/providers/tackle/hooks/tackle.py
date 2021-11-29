"""Tackle hooks."""
import tackle as tkl
import logging
from typing import List, Any
from pydantic import SecretStr

from tackle.models import BaseHook

logger = logging.getLogger(__name__)


class TackleHook(BaseHook):
    """
    Hook  for calling external tackle / cookiecutters.

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

    type: str = 'tackle'

    input_string: str = '.'
    inputs: List[Any] = None
    checkout: str = None
    context_file: str = None
    context_files: list = None
    overwrite_inputs: dict = None
    existing_context: dict = None
    overwrite_if_exists: bool = False
    output_dir: str = '.'
    config_file: str = None
    default_config: str = None
    password: SecretStr = None
    directory: str = None
    directories: List = None
    skip_if_file_exists: bool = False

    _args = ['input_string']

    def execute(self):
        # fmt: off
        output_context = tkl.main.tackle(
            self.input_string,
            checkout=self.checkout,
            existing_context=self.output_dict,
        )
        # fmt: on

        return dict(output_context)


# checkout = self.checkout,
# no_input = self.no_input,
# context_file = self.hook_dict.context_file if 'context_file' in hook_dict else None,
# context_key = self.hook_dict.context_key if 'context_key' in hook_dict else None,
# overwrite_inputs = self.hook_dict.overwrite_inputs if 'overwrite_inputs' in hook_dict else None,
# existing_context = self.hook_dict.existing_context if 'existing_context' in hook_dict else None,
# replay = self.replay,
# rerun = self.rerun,
# record = self.record,
# overwrite_if_exists = self.overwrite_if_exists,
# output_dir = self.hook_dict.output_dir if 'output_dir' in hook_dict else '.',
# default_config = self.default_config,
# password = self.password,
# directory = self.hook_dict.directory if 'directory' in hook_dict else None,
# skip_if_file_exists = self.hook_dict.skip_if_file_exists if 'skip_if_file_exists' in hook_dict else False,
