"""Models for the whole project."""
import logging
from collections import OrderedDict
import yaml
import os
import inspect

# import re

from pathlib import Path

from pydantic import BaseModel, SecretStr, Field, Extra, validator
from typing import Dict, Any, Union, List, Optional, Tuple, Callable

# from typing import Type
# from tackle.render.environment import StrictEnvironment
from tackle.utils.paths import (
    # expand_abbreviations,
    is_repo_url,
    is_file,
    repository_has_tackle_file,
    determine_tackle_generation,
    work_in,
)
from tackle.utils.files import read_config_file, apply_overwrites_to_inputs
from tackle.utils.zipfile import unzip
from tackle.utils.vcs import clone
from tackle.utils.files import load, dump
from tackle.exceptions import (
    InvalidModeException,
    RepositoryNotFound,
    UnknownHookTypeException,
)
from tackle.providers import ProviderList, import_with_fallback_install
from tackle.settings import settings

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import BaseModel

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


# class Provider(BaseModel):
#     """Base provider."""
#
#     path: str = None
#     hooks_path: str = None
#     hook_types: list = []
#     hook_modules: list = []
#
#     name: str = None  # defaults to os.path.basename(path)
#
#     src: str = None
#     version: str = None
#     requirements: list = []


def wrap_jinja_braces(item):
    """Allows for setting a value without {{ value }}"""
    if '{{' not in item and '{{' not in item:
        return '{{' + item + '}}'


# from pydantic.fields import FieldInfo as PydanticFieldInfo
#
# class FieldInfo(PydanticFieldInfo):
#
#     def __init__(self, default: Any = Undefined, **kwargs: Any) -> None:


class HookDict(BaseModel):
    if_: Union[str, bool] = None
    else_: Union[str, bool] = None

    # Python 3.10+
    match_: Any = None
    case_: list = None

    # Retiring
    # when: Union[str, bool] = None
    # loop: Union[str, list] = None

    for_: Union[str, list] = None
    while_: Union[str, bool] = None  # TODO
    enumerate_: Union[str, list] = None  # TODO
    reverse: Union[str, bool] = False

    callback: str = None

    # Order matters here where we want the literal bool to be evaluated first
    merge: Union[bool, str] = None
    # TODO: Move to BaseHook
    confirm: Union[bool, str, dict] = None

    hook_type: str = None

    _args: list = []
    _kwargs: dict = {}
    _flags: list = []

    @validator('if_', 'else_', 'reverse', 'while_', 'for_', 'merge')
    def wrap_bool_if_string(cls, v):
        # import ast
        # x = ast.literal_eval(v)

        if isinstance(v, str):
            return wrap_jinja_braces(v)
        return v

    @validator('match_', 'case_')
    def check_if_using_the_right_python_version(cls, v):
        import sys

        if sys.version_info[1] >= 10:
            return v
        if v is not None:
            logger.info(
                "Must be using Python 3.10+ to use match / case statements. Ignoring."
            )

    # Per https://github.com/samuelcolvin/pydantic/issues/1577
    # See below
    def __setattr__(self, key, val):
        if key in self.__config__.alias_to_fields:
            key = self.__config__.alias_to_fields[key]
        super().__setattr__(key, val)

    class Config:
        extra = 'allow'
        validate_assignment = True
        fields = {
            'hook_type': '<',
            'if_': 'if',
            'else_': 'else',
            'match_': 'match',
            'case_': 'case',
            'for_': 'for',
            'while_': 'while',
            'enumerate_': 'enumerate',
        }

        # Per https://github.com/samuelcolvin/pydantic/issues/1577
        # This is an issue until pydantic 1.9 is released and items can be set with
        # properties which will override the internal __setattr__ method that
        # disregards aliased fields
        alias_to_fields = {v: k for k, v in fields.items()}


class ConfirmHookDict(HookDict):
    """Special case when we want to validate messages/default."""

    message: str = None
    default: str = None


class Context(BaseModel):
    """The main object that is being modified by parsing."""

    config_file: str = None
    config: dict = None
    default_config: bool = False

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

    # TODO: rm
    template_type: str = None

    # input_string: Any = None
    template_name: str = Field(
        None,
        description="The template directory or context file without the extension used "
        "for keying the input dict values.",
    )

    input_string: str = None
    file: str = None  # TODO: Convert to Path type?

    # args: list = []
    # kwargs: dict = {}
    # flags: list = []

    # commands: List[Command] = None
    # command_args: list = None
    # command_kwargs: list = None
    # command_flags: list = None

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

    hook_dict: HookDict = None
    post_gen_hooks: List[Any] = []

    calling_directory: str = os.path.abspath(os.path.curdir)
    rerun_path: str = None

    context_key: str = None

    # value: str = None
    key_path: list = []

    # providers: List[Provider] = None
    # imported_hook_types: List[str] = []

    providers: ProviderList = None

    output_dir: str = '.'
    overwrite_if_exists: bool = False
    skip_if_file_exists: bool = False
    accept_hooks: bool = True
    # TODO: rm
    unrendered_dir: str = None

    # env: Type[StrictEnvironment] = None
    env: Any = None

    # TODO: rm
    # Used in rendering projects
    infile: str = None

    key_: str = None  # The parser's key reference used internally for setting values
    #  and telling the difference between compact vs expanded keys
    _index: int = None  # The parser index used internally for setting values in lists

    _loop_index: int = None  # Used in evaluating loops
    _loop_item: Any = None

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
        # Allows for passing the providers between tackle runtimes
        if self.providers is None:
            # Native and settings.extra_providers initialized
            self.providers = ProviderList()

        # TODO: Move this? -> Since BaseHook inherits from this object we can implement this later...
        if self.existing_context:
            self.output_dict.update(self.existing_context)

    def update_input_dict(self):
        """
        Update the input dict based on the input source.

        TODO:
            - How the input context is keyed and why
            - How context keys are managed
        """

        # Add the Python object to the context dictionary
        # if not self.context_key:
        #     file_name = os.path.split(self.context_file)[1]
        #     self.context_key = file_name.split('.')[0]
        #     self.input_dict[self.context_key] = read_config_file(
        #         os.path.join(self.repo_dir, self.context_file)
        #     )
        # else:
        #     self.input_dict[self.context_key] = read_config_file(
        #         os.path.join(self.repo_dir, self.context_file)
        #     )

        self.input_dict = read_config_file(
            os.path.join(self.repo_dir, self.context_file)
        )

        # Overwrite context variable defaults with the default context from the
        # user's global config, if available
        if settings.default_context:
            apply_overwrites_to_inputs(
                self.input_dict[self.context_key], settings.default_context
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

    def evaluate_rerun(self):
        """Return file or if file does not exist, set record to be true."""
        if os.path.exists(self.rerun_path):
            with open(self.rerun_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            if not self.record:
                print('No rerun file, will create record and use next time.')
                self.record = True


class BaseHook(Context):
    """Base hook class from which all other hooks inherit from to be discovered."""

    type: str = Field(..., description="Name of the hook.")

    chdir: Optional[str] = Field(None, description="Name of the hook.")
    merge: Optional[bool] = False
    confirm: Optional[Any] = False

    _args: Union[List[str], List[Tuple[str, Callable]]] = []
    _kwargs: dict = {}
    _flags: List[str] = {}

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.forbid

    # @validator('_args')
    # def check_this(cls, v):
    #     print()
    #     return v

    def __init__(self, **data: Any):
        super().__init__(**data)
        print()

        # len_args = len(self._args)
        # last_hook_arg_index = len(self._args)

    #     self.evaluate_args()
    #
    # def evaluate_args(self):
    #     i = 0
    #     # num_input_args = len(self.args)
    #     num_input_args = len(self.hook_dict._args)
    #     while i < num_input_args:
    #         if not self._args:
    #             raise ValueError(f"Args provided in key={self.key_} and none allowed "
    #                              f"for hook type {self.type.split()[0]}")
    #
    #         if isinstance(self._args[i], tuple):
    #             if i + 1 == len(self._args):
    #                 # We are at the last argument mapping so we need to join the remaining
    #                 # arguments as a single string. Was parsed on spaces so reconstructed.
    #
    #                 # if isinstance(self.hook_dict._args[- ict._args[-1])
    #
    #                 input_arg = self.hook_dict._args[-1]
    #
    #
    #                 # Set the mapped argument in the hook to the last argument
    #                 setattr(self, self._args[i][0], self._args[i][1](input_arg))
    #                 # Also set the value in the hook dict as in special circumstances like
    #                 # the tackle file
    #                 setattr(self.hook_dict, self._args[i][0], self._args[i][1](input_arg))
    #                 # self.hook_dict[self._args[i][0]] = self._args[i][1](input_arg)
    #                 return
    #             else:
    #                 # The hooks arguments are indexed
    #                 input_arg = self.hook_dict._args[i]
    #
    #                 # Set the mapped argument in the hook to the last arument
    #
    #                 x = self._args[i][1]
    #
    #                 setattr(self, self._args[i][0], self._args[i][1](input_arg))
    #                 setattr(self.hook_dict, self._args[i][0], self._args[i][1](input_arg))
    #                 # self.hook_dict[self._args[i][0]] = self._args[i][1](input_arg)
    #                 print()
    #         i += 1

    # Remove all the args so they don't get overloaded on the next hook
    # instantiation
    # self.args = []

    def execute(self) -> Any:
        raise NotImplementedError("Every hook needs an execute method.")

    def call(self) -> Any:
        """
        Call main entrypoint to calling hook.

        Handles `chdir` method.
        """
        if self.chdir:
            path = os.path.abspath(os.path.expanduser(self.chdir))
            if os.path.isdir(path):
                # Use contextlib to switch dirs
                with work_in(os.path.abspath(os.path.expanduser(self.chdir))):
                    return self.execute()
            else:
                raise NotADirectoryError(
                    f"The specified path='{path}' to change to was not found."
                )
        else:
            return self.execute()

        # self.unpack_input_string()

    # repo_dir: str = None
    # template_name: str = None
    # tackle_gen: TackleGen = TackleGen.tackle
    # cleanup: bool = False

    # def unpack_input_string(self):
    #     """
    #     Take the input template and unpack the args and kwargs if they exist.
    #     Updates the command_args and command_kwargs with a list of strings and
    #     list of dicts respectively.
    #     """
    #     if self.input_string is None:
    #         print()
    #         return
    #
    #     input_list = self.input_string.split()
    #     input_list_length = len(input_list)
    #     # args = []
    #     # kwargs = []
    #     # flags = []
    #
    #     i = 0
    #     while i < input_list_length:
    #         raw_arg = input_list[i]
    #         if i + 1 < input_list_length:
    #             next_raw_arg = input_list[i + 1]
    #         else:
    #             # Allows logic for if last item has `--` in it then it is a flag
    #             next_raw_arg = "-"
    #
    #         if (raw_arg.startswith('--') or raw_arg.startswith('-')) and not next_raw_arg.startswith('-'):
    #             # Field is a kwarg
    #             self.kwargs.update({raw_arg: input_list[i + 1]})
    #             i += 1
    #         elif (raw_arg.startswith('--') or raw_arg.startswith('-')) and next_raw_arg.startswith('-'):
    #             # Field is a flag
    #             self.flags.append(raw_arg)
    #         else:
    #             # Field is an argument
    #             self.args.append(raw_arg)
    #         i += 1
    #
