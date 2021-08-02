"""Models for the whole project."""
import logging
from collections import OrderedDict
import os
import re
from pathlib import Path

from pydantic import BaseModel, SecretStr, Extra, validator
from typing import Dict, Any, Union, Type, List, Optional

from tackle.render.environment import StrictEnvironment
from tackle.utils.paths import (
    expand_abbreviations,
    is_repo_url,
    is_file,
    repository_has_tackle_file,
    determine_tackle_generation, work_in,
)
from tackle.utils.files import read_config_file, apply_overwrites_to_inputs
from tackle.utils.zipfile import unzip
from tackle.utils.vcs import clone
from tackle.exceptions import InvalidModeException, RepositoryNotFound
from tackle.settings import Settings

logger = logging.getLogger(__name__)

USER_CONFIG_PATH = os.path.expanduser('~/.tacklerc')

DEFAULT_ABBREVIATIONS: Dict = {
    'gh': 'https://github.com/{0}.git',
    'gl': 'https://gitlab.com/{0}.git',
    'bb': 'https://bitbucket.org/{0}',
}

CONTEXT_FILE_DICT = {
    'cookiecutter': [
        'cookiecutter.json',
        'cookiecutter.yaml',
        'cookiecutter.yml',
        'cookiecutter.hcl',
    ],
    'tackle': [
        '.tackle.yaml',
        '.tackle.yml',
        '.tackle.json',
        '.tackle.hcl',
        'tackle.yaml',
        'tackle.yml',
        'tackle.json',
        'tackle.hcl',
    ],
}

ALL_VALID_CONTEXT_FILES = (
    CONTEXT_FILE_DICT['cookiecutter'] + CONTEXT_FILE_DICT['tackle']
)


class Provider(BaseModel):
    """Base provider."""

    path: str = None
    hooks_path: str = None
    hook_types: list = []
    hook_modules: list = []

    name: str = None  # defaults to os.path.basename(path)

    src: str = None
    version: str = None
    requirements: list = []


class Context(BaseModel):
    """The main object that is being modified by parsing."""

    settings: Settings = None

    # Mode
    no_input: bool = False
    replay: bool = None
    record: Union[bool, str] = None
    rerun: Union[bool, str] = None

    # Source
    password: SecretStr = None
    directory: str = None
    repo: str = None
    repo_dir: Path = None

    template_type: str = None
    template: str = "."
    template_name: str = None
    checkout: str = None
    context_file: str = None
    cleanup: bool = False
    tackle_gen: str = None

    # Context
    existing_context: Union[Dict, OrderedDict] = None
    overwrite_inputs: Union[dict, str] = None
    override_inputs: Union[Dict, str] = None

    input_dict: OrderedDict = OrderedDict([])
    output_dict: OrderedDict = OrderedDict([])

    hook_dict: OrderedDict = None
    post_gen_hooks: List[Any] = []

    calling_directory: str = os.path.abspath(os.path.curdir)
    rerun_path: str = None

    context_key: str = None
    key: str = None

    providers: List[Provider] = None
    imported_hook_types: List[str] = []

    @validator('template')
    def template_expand_abbreviations(cls, v, values, **kwargs):
        return expand_abbreviations(v, values['settings'].abbreviations)

    @validator('template')
    def update_template_if_has_single_slash(cls, v):
        """
        Check if the template has a single slash, then check if it is a path,
        otherwise it is github repo and the full path is prepended.
        """
        REPO_REGEX = re.compile(
            r"""/^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$/i""",
            re.VERBOSE,
        )
        if os.path.exists(v):
            # Path reference
            return v
        if REPO_REGEX.match(v):
            return v
        # TODO - Test this, seems broken
        return v

    @validator('replay')
    def validate_rerun_and_replay_both_not_set(cls, v, values):
        """Validate that the replay / rerun mode."""
        if v and values['rerun']:
            err_msg = "You can not use both replay and rerun at the same time."
            raise InvalidModeException(err_msg)
        else:
            return v

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.existing_context:
            self.output_dict.update(self.existing_context)

    def update_source(self):
        """
        Locate the repository directory from a template reference.

        If the template refers to a zip file or zip url, download / unzip as the context.
        If the template refers to a repository URL, clone it.
        If the template refers to a file, use that as the context.
        If the template is a path to a local repository, use it.
        """
        # Zipfile
        if self.template.lower().endswith('.zip'):
            unzipped_dir = unzip(
                zip_uri=self.template,
                clone_to_dir=self.settings.tackle_dir,
                no_input=self.no_input,
                password=self.password,
            )
            repository_candidates = [unzipped_dir]
            self.cleanup = True
        # Repo
        elif is_repo_url(self.template):
            cloned_repo = clone(
                repo_url=self.template,
                checkout=self.checkout,
                clone_to_dir=self.settings.tackle_dir,
                no_input=self.no_input,
            )
            repository_candidates = [cloned_repo]
        # File
        elif is_file(self.template):
            # Special case where the input is a path to a file
            self.context_file = os.path.basename(self.template)
            self.repo_dir = Path(self.template).parent.absolute()
            self.template_name = os.path.basename(os.path.abspath(self.repo_dir))
            self.tackle_gen = determine_tackle_generation(self.context_file)
            return
        else:
            # Search in potential locations
            repository_candidates = [
                self.template,
                os.path.join(self.settings.tackle_dir, self.template),
            ]

        if self.directory:
            repository_candidates = [
                os.path.join(s, self.directory) for s in repository_candidates
            ]

        for repo_candidate in repository_candidates:
            self.context_file = repository_has_tackle_file(
                repo_candidate, self.context_file
            )
            if not self.context_file:
                # Means that no valid context file has been found or provided
                continue
            else:
                self.repo_dir = Path(os.path.abspath(repo_candidate))
                self.template_name = os.path.basename(os.path.abspath(repo_candidate))
                self.tackle_gen = determine_tackle_generation(self.context_file)
                return

        raise RepositoryNotFound(
            'A valid repository for "{}" could not be found in the following '
            'locations:\n{}'.format(self.template, '\n'.join(repository_candidates))
        )

    def update_input_dict(self):
        """
        Update the input dict based on the input source.

        TODO:
            - How the input context is keyed and why
            - How context keys are managed
        """

        # Add the Python object to the context dictionary
        if not self.context_key:
            file_name = os.path.split(self.context_file)[1]
            self.context_key = file_name.split('.')[0]
            self.input_dict[self.context_key] = read_config_file(
                os.path.join(self.repo_dir, self.context_file)
            )
        else:
            self.input_dict[self.context_key] = read_config_file(
                os.path.join(self.repo_dir, self.context_file)
            )

        # Overwrite context variable defaults with the default context from the
        # user's global config, if available
        if self.settings.default_context:
            apply_overwrites_to_inputs(
                self.input_dict[self.context_key], self.settings.default_context
            )

        # Apply the overwrites
        # Strings are interpreted as pointers to files and converted to dict
        if isinstance(self.overwrite_inputs, str):
            self.overwrite_inputs = read_config_file(self.overwrite_inputs)
        if self.overwrite_inputs:
            apply_overwrites_to_inputs(
                self.input_dict[self.context_key], self.overwrite_inputs
            )

        # TODO: Integrate overwrite logic to `output_dict`
        # Should pop the inputs and insert itself into the input dict
        if isinstance(self.override_inputs, str):
            self.override_inputs = read_config_file(self.override_inputs)
        if self.override_inputs:
            apply_overwrites_to_inputs(
                self.output_dict[self.context_key], self.override_inputs
            )
            for k, _ in self.override_inputs:
                self.input_dict.pop(k)


class BaseHook(Context):
    """Base hook mixin class."""

    chdir: Optional[str] = None
    merge: Optional[bool] = False
    post_gen_hook: Optional[bool] = False
    confirm: Optional[Any] = False

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.forbid
        # orm_mode = True

    def execute(self) -> Any:
        raise NotImplementedError("Every hook needs an execute method.")

    def call(self) -> Any:
        """
        Call main entrypoint to calling hook.

        Handles `chdir` method.
        """
        if self.chdir:
            if os.path.isdir(os.path.abspath(os.path.expanduser(self.chdir))):
                # Use contextlib to switch dirs and come back out
                with work_in(os.path.abspath(os.path.expanduser(self.chdir))):
                    return self.execute()
            else:
                raise NotADirectoryError("The specified path to change to was not found.")
        else:
            return self.execute()


class Output(BaseModel):
    """Output model."""

    output_dir: str = '.'
    overwrite_if_exists: bool = False
    skip_if_file_exists: bool = False
    accept_hooks: bool = True
    unrendered_dir: str = None
    env: Type[StrictEnvironment] = None
    infile: str = None
