# -*- coding: utf-8 -*-

"""Operator plugin that inherits a base class and is made available through `type`."""
from __future__ import unicode_literals
from __future__ import print_function

import cookiecutter as cc
import logging
from typing import Dict, List, Any
from pydantic import SecretStr

from cookiecutter.models import BaseHook

logger = logging.getLogger(__name__)


class NukikataOperator(BaseHook):
    """
    Operator for calling external tackle / cookiecutters.

    :param template: A directory containing a project template,
        or a URL to a git repository.
    :param templates: A list of directories containing a project template,
        or a URL to a git repository.
    :param checkout: The branch, tag or commit ID to checkout after clone.
    :param no_input: Prompt the user at command line for manual configuration?
    :param extra_context: A dictionary of context that overrides default
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
    :param directory: Relative path to a cookiecutter template in a repository.
    :param accept_hooks: Accept pre and post hooks if set to `True`.

    :return: Dictionary of output
    """

    type: str = 'tackle'

    template: Any = '.'
    templates: List[Any] = None
    checkout: str = None
    no_input: bool = False
    context_file: str = None
    context_files: List = None
    existing_context: Dict = None
    extra_context: Dict = None
    replay: bool = None
    overwrite_if_exists: bool = False
    output_dir: str = '.'
    config_file: str = None
    default_config: str = None
    password: SecretStr = None
    directory: str = None
    directories: List = None
    skip_if_file_exists: bool = False

    def execute(self):

        #  Run all the loops
        if not self.templates and not self.directories and not self.context_files:
            return self._run_tackle()

        output = {}
        if self.templates:
            for i in self.templates:
                self.template = i
                output.update({i: self._run_tackle()})

        if self.directories:
            for i in self.directories:
                self.directory = i
                output.update({i: self._run_tackle()})

        if self.context_files:
            for i in self.context_files:
                self.context_file = i
                output.update({i: self._run_tackle()})

        return output

    def _run_tackle(self):
        output_context = cc.main.cookiecutter(
            template=self.template,
            checkout=self.checkout,
            no_input=self.no_input,
            context_file=self.context_file,
            context_key=self.context_key,
            existing_context=self.existing_context,
            extra_context=self.extra_context,
            replay=self.replay,
            overwrite_if_exists=self.overwrite_if_exists,
            output_dir=self.output_dir,
            config_file=self.config_file,
            default_config=self.default_config,
            password=self.password,
            directory=self.directory,
            skip_if_file_exists=self.skip_if_file_exists,
        )

        return output_context
