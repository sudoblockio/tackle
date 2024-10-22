from __future__ import annotations

from dataclasses import dataclass

from jinja2 import StrictUndefined
from jinja2.nativetypes import NativeEnvironment
from jinja2.nativetypes import NativeEnvironment as Environment

from tackle.models import GenericHookType
from tackle.types import DocumentObjectType, DocumentType


@dataclass
class Source:
    input_string: str | None = None
    checkout: str | None = None
    latest: bool | None = None
    find_in_parent: bool | None = None
    directory: str | None = None
    calling_directory: str | None = None
    file: str | None = None
    base_dir: str | None = None
    hooks_dir: str | None = None
    name: str | None = None
    raw: dict | list = None


@dataclass
class Data:
    input: DocumentType | None = None
    raw_input: DocumentType | None = None
    pre_input: DocumentType | None = None
    post_input: DocumentType | None = None
    hooks_input: DocumentObjectType | None = None
    public: DocumentType | None = None
    private: DocumentType | None = None
    temporary: DocumentType | None = None
    existing: DocumentObjectType | None = None
    overrides: DocumentObjectType | None = None


@dataclass
class Paths:
    current: Source = None
    calling: Source = None
    tackle: Source = None


@dataclass
class InputArguments:
    args: list = None
    kwargs: dict = None
    help_string: str = ""


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
    input: InputArguments | None = None
    source: Source | None = None
    hooks: Hooks | None = None
    data: Data | None = None
    path: Paths | None = None

    # Flag to denote to exit parsing
    break_: bool = False
    # Hold the environment in the context
    # env_: Environment = StrictEnvironment()
    env_: Environment = NativeEnvironment(undefined=StrictUndefined)
