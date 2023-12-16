from typing import Optional, Union

from jinja2 import Environment, StrictUndefined
# from jinja2 import StrictUndefined
from jinja2.nativetypes import NativeEnvironment as Environment
from jinja2.nativetypes import NativeEnvironment

from dataclasses import dataclass

from tackle.types import DocumentType, DocumentObjectType
from tackle.models import GenericHookType


@dataclass
class Source:
    input_string: Optional[str] = None
    checkout: Optional[str] = None
    latest: Optional[bool] = None
    find_in_parent: Optional[bool] = None
    directory: Optional[str] = None
    file: Optional[str] = None
    base_dir: Optional[str] = None
    hooks_dir: Optional[str] = None
    name: Optional[str] = None
    raw: Union[dict, list] = None


@dataclass
class Data:
    input: Optional[DocumentType] = None
    raw_input: Optional[DocumentType] = None
    pre_input: Optional[DocumentType] = None
    post_input: Optional[DocumentType] = None
    hooks_input: Optional[DocumentObjectType] = None
    public: Optional[DocumentType] = None
    private: Optional[DocumentType] = None
    temporary: Optional[DocumentType] = None
    existing: Optional[DocumentObjectType] = None
    overrides: Optional[DocumentObjectType] = None


@dataclass
class Paths:
    current: Source = None
    calling: Source = None
    tackle: Source = None


@dataclass
class InputArguments:
    args: list = None
    kwargs: dict = None


class StrictEnvironment(Environment):
    """
    Strict Jinja2 environment. Will raise error on undefined variable in template
     rendering.
    """

    def __init__(self, **kwargs):
        super(StrictEnvironment, self).__init__(undefined=StrictUndefined, **kwargs)


@dataclass
class HookMethods:
    public: dict[GenericHookType] = None
    private: dict[GenericHookType] = None
    default: dict = None


@dataclass
class Hooks:
    """Collection of hooks to call. Kept generic to break circular dependency."""

    public: dict[str, 'GenericHookType'] = None
    private: dict[str, 'GenericHookType'] = None
    native: dict[str, 'GenericHookType'] = None
    default: dict = None


@dataclass
class Context:
    """Main container for all data passed through tackle."""
    # Flag to indicate the user doesn't want to be prompted thereby choosing
    # defaults for any available prompt
    no_input: bool = False
    # Flag to verbosely print out logs
    verbose: bool = False
    # A list of parsed keys in an object / or byte encoded indexes for items in an
    # array. Used to track position within a document.
    key_path: list = None
    # An indexed version of the key path used within blocks to maintain temporary
    # data for rendering. See [docs]()
    key_path_block: list = None

    # Internal data objects
    input: Optional[InputArguments] = None
    source: Optional[Source] = None
    hooks: Optional[Hooks] = None
    data: Optional[Data] = None
    path: Optional[Paths] = None

    # Flag to denote to exit parsing
    break_: bool = False
    # Hold the environment in the context
    # env_: Environment = StrictEnvironment()
    env_: Environment = NativeEnvironment(undefined=StrictUndefined)
