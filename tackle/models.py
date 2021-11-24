"""Models for the whole project."""
import logging
from collections import OrderedDict
import os
from pathlib import Path
from pydantic import BaseModel, SecretStr, Field, Extra, validator, PrivateAttr
from typing import Dict, Any, Union, List, Optional, Tuple, Callable

from tackle.utils.paths import work_in
from tackle.exceptions import InvalidModeException
from tackle.providers import ProviderList

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


def wrap_jinja_braces(item):
    """Allows for setting a value without {{ value }}"""
    if '{{' not in item and '{{' not in item:
        return '{{' + item + '}}'


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

    # Mode
    no_input: bool = False

    # Source
    password_: SecretStr = None
    directory_: str = None
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
    version_: str = Field(
        None,
        description="For inputs referencing remote repos, this refers to "
        "a branch or tag.",
    )
    context_file: str = None
    cleanup: bool = False
    # Context
    existing_context: Union[Dict, OrderedDict] = None
    overwrite_inputs: Union[dict, str] = None
    override_inputs: Union[Dict, str] = None

    input_dict: OrderedDict = OrderedDict([])
    output_dict: OrderedDict = OrderedDict([])
    remove_key_list: list = []

    hook_dict: HookDict = None
    post_gen_hooks: List[Any] = []

    calling_directory: str = os.path.abspath(os.path.curdir)
    rerun_path: str = None

    context_key: str = None

    element_: Any = None
    key_path: list = []
    key_dict_: dict = Field(
        {},
        description="This is the dict that stores key paths as keys and hooks as "
        "values. For topological sorting of keys.",
    )

    providers: ProviderList = None
    output_dir: str = '.'
    overwrite_if_exists: bool = False
    skip_if_file_exists: bool = False
    accept_hooks: bool = True

    # TODO: Make private
    env: Any = None

    # TODO: rm
    unrendered_dir: str = None
    # Used in rendering projects
    infile: str = None

    # TODO: rm
    key_: str = None  # The parser's key reference used internally for setting values
    #  and telling the difference between compact vs expanded keys

    # _index: int = Field(None, description="The parser index used internally for setting values in lists")
    loop_index: int = Field(None)
    loop_item: Any = Field(None)

    # class Config:
    #     fields = {
    #         'version_': 'version',
    #     }

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Allows for passing the providers between tackle runtimes

        # TODO: Make this async?
        # import time
        # time_start = time.time()
        if self.providers is None:
            # Native and settings.extra_providers initialized
            self.providers = ProviderList()
        # x = time.time() - time_start
        # print(x)

        # TODO: Move this? -> Since BaseHook inherits from this object we can implement this later...
        if self.existing_context:
            self.output_dict.update(self.existing_context)


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

    def __init__(self, **data: Any):
        super().__init__(**data)

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
