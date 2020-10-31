"""Models for the whole project."""
from pydantic import BaseModel, SecretStr
from typing import Dict, Any, Union, Type, List
from cookiecutter.exceptions import InvalidModeException
from cookiecutter.render.environment import StrictEnvironment

from collections import OrderedDict
import os
from enum import Enum


class TackleGen(str, Enum):
    """Tackel generation, placeholder for successive parsers."""

    cookiecutter = 'cookiecutter'
    tackle = 'tackle'


class Context(BaseModel):
    """The main object that is being modifed by parsing."""

    context_file: str = None
    context_key: str = None  # os.path.basename(context_file).split('.')[0]
    key: str = None

    existing_context: Dict = None
    extra_context: Dict = None
    input_dict: OrderedDict = None
    output_dict: OrderedDict = None
    hook_dict: OrderedDict = None

    post_gen_hooks: List[Any] = []

    env: Type[StrictEnvironment] = None

    calling_directory = os.path.abspath(os.getcwd())
    tackle_gen: str = None

    def __init__(self, **data: Any):
        super().__init__(**data)


class Mode(BaseModel):
    """Mode in which the project is run."""

    no_input: bool = False
    replay: Union[bool, str] = None
    record: Union[bool, str] = None
    rerun: bool = None
    overwrite_if_exists: bool = False
    skip_if_file_exists: bool = False
    accept_hooks: bool = True
    output_dir: str = '.'

    class Config:
        allow_mutation = False

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.replay and self.no_input:
            err_msg = (
                "You can not use both replay and no_input or extra_context "
                "at the same time."
            )
            raise InvalidModeException(err_msg)


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


class Output(BaseModel):
    """Output model."""

    output_dir: str = '.'
    overwrite_if_exists: bool = False
    skip_if_file_exists: bool = False
    accept_hooks: bool = True
    unrendered_dir: str = None
    env: Type[StrictEnvironment] = None
    infile: str = None
