"""Models for the whole project."""
from collections import OrderedDict
import os
from enum import Enum

from pydantic import BaseModel, SecretStr, BaseSettings, Extra
from typing import Dict, Any, Union, Type, List, Optional

from tackle.render.environment import StrictEnvironment
from tackle.utils.paths import expand_path
from tackle.utils.context_manager import work_in

USER_CONFIG_PATH = os.path.expanduser('~/.tacklerc')

DEFAULT_ABBREVIATIONS: Dict = {
    'gh': 'https://github.com/{0}.git',
    'gl': 'https://gitlab.com/{0}.git',
    'bb': 'https://bitbucket.org/{0}',
}


class Settings(BaseSettings):
    """Base settings for run."""

    tackle_dir: str = '~/.tackle'
    replay_dir: str = os.path.join(tackle_dir, 'replay')

    rerun_file_suffix: str = 'rerun.yml'

    abbreviations: Dict = {}
    default_context: Dict = OrderedDict([])

    config_path: str = None

    extra_providers: list = None
    dump_output: str = 'yaml'

    class Config:
        env_prefix = 'TACKLE_'
        env_file_encoding = 'utf-8'

    def __init__(self, **values: Any):
        super().__init__(**values)
        self.abbreviations.update(DEFAULT_ABBREVIATIONS)

        self.tackle_dir = expand_path(self.tackle_dir)
        self.replay_dir = expand_path(self.replay_dir)


class TackleGen(str, Enum):
    """Tackel generation, placeholder for successive parsers."""

    cookiecutter = 'cookiecutter'
    tackle = 'tackle'


class Mode(BaseModel):
    """Mode in which the project is run."""

    no_input: bool = False
    replay: Union[bool, str] = None
    record: Union[bool, str] = None
    rerun: Union[bool, str] = None


class Source(BaseModel):
    """Source attributes model."""

    template: str = "."
    template_name: str = None
    checkout: str = None
    context_file: str = None
    cleanup: bool = False
    tackle_gen: str = None  # This attr is copied over to 'Context' for convenience

    password: SecretStr = None
    directory: str = None
    repo: str = None

    repo_dir: str = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.context_file:
            self.context_file = os.path.expanduser(
                os.path.expandvars(self.context_file)
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

    # context_file: str = None
    context_key: str = None
    key: str = None

    input_dict: OrderedDict = OrderedDict([])
    output_dict: OrderedDict = None

    existing_context: Union[Dict, OrderedDict] = None
    overwrite_inputs: Union[dict, str] = None
    override_inputs: Union[Dict, str] = None

    hook_dict: OrderedDict = None
    post_gen_hooks: List[Any] = []

    calling_directory: str = None
    rerun_path: str = None
    tackle_gen: str = None

    providers: List[Provider] = []
    imported_hook_types: List[str] = []


class BaseHook(Context, Mode):
    """Base hook mixin class."""

    chdir: Optional[str] = None
    merge: Optional[bool] = False
    post_gen_hook: Optional[bool] = False
    confirm: Optional[str] = False

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.forbid
        # orm_mode = True

    def execute(self) -> Any:
        """Abstract method."""
        raise NotImplementedError()

    def call(self) -> Any:
        """
        Call main entrypoint to calling hook.

        Handles `chdir` method.
        """
        if self.chdir and os.path.isdir(
            os.path.abspath(os.path.expanduser(self.chdir))
        ):
            # Use contextlib to switch dirs and come back out
            with work_in(os.path.abspath(os.path.expanduser(self.chdir))):
                return self.execute()
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
