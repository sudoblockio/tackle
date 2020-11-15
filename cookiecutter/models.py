"""Models for the whole project."""
from pydantic import BaseModel, SecretStr
from typing import Dict, Any, Union, Type, List
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


class Output(BaseModel):
    """Output model."""

    output_dir: str = '.'
    overwrite_if_exists: bool = False
    skip_if_file_exists: bool = False
    accept_hooks: bool = True
    unrendered_dir: str = None
    env: Type[StrictEnvironment] = None
    infile: str = None
