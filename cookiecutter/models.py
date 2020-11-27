"""Models for the whole project."""
from collections import OrderedDict
import os
from enum import Enum
from pydantic import BaseModel, SecretStr, BaseSettings
from typing import Dict, Any, Union, Type, List

from cookiecutter.render.environment import StrictEnvironment
from cookiecutter.utils.paths import expand_path


USER_CONFIG_PATH = os.path.expanduser('~/.cookiecutterrc')

DEFAULT_ABBREVIATIONS: Dict = {
    'gh': 'https://github.com/{0}.git',
    'gl': 'https://gitlab.com/{0}.git',
    'bb': 'https://bitbucket.org/{0}',
}


# def expand_path(path):
#     """Expand both environment variables and user home in the given path."""
#     path = os.path.expandvars(path)
#     path = os.path.expanduser(path)
#     return path


class Settings(BaseSettings):
    """Base settings for run."""

    cookiecutters_dir: str = '~/.cookiecutters/'
    replay_dir: str = '~/.cookiecutter_replay/'

    tackle_dir: str = '~/.tackle-box'

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

        self.cookiecutters_dir = expand_path(self.cookiecutters_dir)
        self.replay_dir = expand_path(self.replay_dir)

    def init(self):
        print()
        pass


class TackleGen(str, Enum):
    """Tackel generation, placeholder for successive parsers."""

    cookiecutter = 'cookiecutter'
    tackle = 'tackle'


class Context(BaseModel):
    """The main object that is being modified by parsing."""

    context_file: str = None
    context_key: str = None
    key: str = None

    input_dict: OrderedDict = None
    output_dict: OrderedDict = None

    existing_context: Dict = None
    overwrite_inputs: Dict = None
    override_inputs: Dict = None

    hook_dict: OrderedDict = None
    post_gen_hooks: List[Any] = []

    env: Type[StrictEnvironment] = None

    calling_directory: str = None
    tackle_gen: str = None

    # providers: Field[Providers]


class Mode(BaseModel):
    """Mode in which the project is run."""

    no_input: bool = False
    replay: Union[bool, str] = None
    record: Union[bool, str] = None
    rerun: Union[bool, str] = None
    overwrite_if_exists: bool = False
    skip_if_file_exists: bool = False
    accept_hooks: bool = True
    output_dir: str = '.'

    # class Config:
    #     allow_mutation = False


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
    path_hooks: str = None
    name: str = None
    src: str = None
    version: str = None
    hook_types: list = []
    requirements: list = []


class Providers(BaseModel):
    """Collection of providers."""

    providers: List[Provider] = []
    provider_paths: list = []
    settings_providers: List[Provider] = []
    all_hook_types: list = []

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Initialize the native providers
        for i in [
            os.path.abspath(n)
            for n in os.listdir(os.path.join(os.path.dirname(__file__), 'providers'))
            if os.path.isdir(os.path.join(os.path.dirname(__file__), 'providers', n))
        ]:
            self.provider_paths.append(i)


class Output(BaseModel):
    """Output model."""

    output_dir: str = '.'
    overwrite_if_exists: bool = False
    skip_if_file_exists: bool = False
    accept_hooks: bool = True
    unrendered_dir: str = None
    env: Type[StrictEnvironment] = None
    infile: str = None
