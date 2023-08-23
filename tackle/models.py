from abc import ABC
from jinja2 import Environment, StrictUndefined
from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
    ConfigDict,
)
from pydantic._internal._model_construction import ModelMetaclass
from typing import (
    Any,
    Union,
    Optional,
    Callable,
    Literal,
    Type,
)

from tackle.pydantic.fields import Field
from tackle.pydantic.validators import DclHookValidator
from tackle.pydantic.config import DclHookModelConfig
from tackle.types import (
    DocumentType,
    DocumentObjectType,
)


class LazyImportHook(BaseModel):
    """Object to hold hook metadata so that it can be imported only when called."""

    hooks_path: str
    mod_name: str
    provider_name: str
    hook_type: str
    is_public: bool = False

    def wrapped_exec(self, **kwargs):
        kwargs['provider_hooks'].import_with_fallback_install(
            mod_name=self.mod_name,
            hooks_directory=self.hooks_path,
        )
        return kwargs['provider_hooks'][self.hook_type].wrapped_exec()


class LazyBaseHook(BaseModel):
    """
    Base class that declarative hooks are derived from and either imported when a
     tackle file is read (by searching in adjacent hooks directory) or on init in local
     providers. Used by jinja extensions and filters.
    """
    input_raw: dict = Field(
        ...,
        description="A dict for the lazy function to be parsed at runtime. Serves as a "
                    "carrier for the function's schema until it is compiled with "
                    "`create_function_model`.",
    )
    hook_fields: set = Field(
        set(),
        description="List of fields used to 1, enrich functions without exec method, "
                    "and 2, inherit base attributes into methods. Basically a helper.",
    )
    is_public: bool = Field(..., description="Public or private.")


class TackleLockHook(BaseModel):
    public: dict[str, Union[LazyBaseHook, LazyImportHook]] = {}
    private: dict[str, Union[LazyBaseHook, LazyImportHook]] = {}


class TackleLockProvider(BaseModel):
    type: str = None
    version: str = None
    path: str = None
    hooks: dict[str, TackleLockHook] = {}


class TackleLock(BaseModel):
    tackle_version: str
    provider_dir: str = None
    providers: list[TackleLockProvider] = []
    hooks: TackleLockHook = {}


class PythonRequirement(BaseModel):
    package_name: str
    version: str = 'latest'


class Source(BaseModel):
    input_string: str = Field(None, description="")

    checkout: str = Field(None, description="")
    latest: bool = Field(None, description="")
    find_in_parent: bool = Field(None, description="")

    directory: str = Field(None, description="")
    file: str = Field(None, description="Set as kwarg or ")

    base_dir: str = Field(None, description="")
    hooks_dir: str = Field(None, description="")
    name: str = Field(None, description="")


class Data(BaseModel):
    input: DocumentType = Field(None)

    raw_input: DocumentType = Field(None)
    pre_input: DocumentType = Field(None)
    post_input: DocumentType = Field(None)
    hooks_input: DocumentObjectType = Field(None)

    public: DocumentType = Field(None)
    private: DocumentType = Field(None)
    temporary: DocumentType = Field(None)
    existing: DocumentObjectType = Field(None)

    overrides: DocumentObjectType = Field(None)


class Paths(BaseModel):
    """
    Object to keep track of the current and prior set of paths that tackle was called
     in. Very useful when calling multiple tackle providers that
    context.source.current.path
    """
    current: Source = Field(None, description="Current tackle provider.")
    calling: Source = Field(None, description="The originally called provider.")
    tackle: Source = Field(None, description="??? - There was a reason...")


class InputArguments(BaseModel):
    args: list = Field(None, description="")
    kwargs: dict = Field(None, description="")


class StrictEnvironment(Environment):
    """Create strict Jinja2 environment.

    Jinja2 environment will raise error on undefined variable in template-
    rendering context.
    """

    def __init__(self, **kwargs):
        super(StrictEnvironment, self).__init__(undefined=StrictUndefined, **kwargs)
        # TODO: Add imports for jinja hook filters


class HookBase(BaseModel):
    help: str | None = Field(
        None,
        description="A string to display when calling with the `help` argument."
    )
    render_by_default: list | None = Field(
        None,
        description="A list of fields to wrap with jinja braces and render by default."
    )
    render_exclude: list | None = Field(
        None,
        description="A list of field names to not render."
    )
    is_public: list | None = Field(
        None,
        description="A boolean if hook is public / callable from outside the provider)."
    )
    skip_output: bool | None = Field(
        False,
        description="A flag to skip the output and not set the key. Can also be set"
                    " within a hook call."
    )
    no_input: bool | None = Field(
        False,
        description="A flag to skip any prompting. Can also be set from command line.",
        render_by_default=True,
    )
    args: list[str] | None = Field(
        None,
        description="A list of fields map arguments. See [docs]() for details."
    )
    kwargs: str | None = Field(
        None,
        description="A field name of type dict to map additional arguments to."
    )
    literal_fields: list[str] | None = Field(
        None,
        description="A list of fields to use without."
    )


class HookCallInput(BaseModel):
    """
    Deserializer for hook base methods. Takes all the extra key value pairs and puts
     them into the hook_dict.
    """
    if_: Union[str, bool, type(None)] = Field(
        None,
        description="Conditional evaluated within a loop. Strings rendered by default.",
        render_by_default=True,
        alias='if',
    )
    else_: Any = Field(
        None,
        description="Data to parse for a negative `if` or `when` condition.",
        alias='else',
        render_exclude=True,
    )
    when: Union[str, bool, type(None)] = Field(
        None,
        description="Conditional evaluated before a loop. Strings rendered by default.",
        render_by_default=True,
    )
    for_: Union[str, list, dict, type(None)] = Field(
        None,
        description="Loop over items in a list or keys and values in a dict.",
        render_by_default=True,
        alias='for',
    )
    reverse: Union[str, bool, type(None)] = Field(
        None,
        description="With `for` loops, iterate in reverse.",
        render_by_default=True,
    )
    try_: Union[str, bool, type(None)] = Field(
        None,
        description="Catch errors of hook call. Can be used with except.",
        render_by_default=True,
        alias='try',
    )
    except_: Any = Field(
        None,
        description="Data to parse when encountering an error for `try`.",
        render_by_default=True,
        alias='except',
    )
    chdir: Optional[str] = Field(
        None,
        description="Change directory while executing the hook returning after.",
        alias="cd"
    )
    merge: Union[bool, str, type(None)] = Field(
        None,
        description="Merge result to the parent key for objects or append if a list.",
        render_by_default=True,
    )
    confirm: Union[bool, str, dict, type(None)] = Field(
        None,
        description="Change directory while executing the hook returning after.",
        render_by_default=True,
    )
    kwargs: Union[str, dict, type(None)] = Field(
        None,
        description="A dict to map to inputs for a hook. Strings rendered by default.",
        render_by_default=True,
    )
    skip_output: bool | None = Field(
        False,
        description="A flag to not set the key. Can also be set in hook definition.",
        render_by_default=True,
    )
    no_input: bool | None = Field(
        False,
        description="A flag to skip any prompting. Can also be set from command line.",
        render_by_default=True,
    )

    # Populated from extra vars in validator
    hook_dict: dict = Field(
        ...,
        description="Dict of all extra fields.",
    )

    @model_validator(mode='before')
    def build_hook_dict(cls, values: dict[str, Any]) -> dict[str, Any]:
        extra: dict[str, Any] = {}
        for field_name in list(values):
            if field_name not in cls.model_fields:
                extra[field_name] = values.pop(field_name)
        values['hook_dict'] = extra
        return values


# Note we have a circular dependency between BaseHook having Context and Context having
# Hooks which is a collection of BaseHooks. We prefer carrying Context into BaseHook
# since this is user facing so breaking circular dependency here with ModelMetaclass
GenericHookType = Union[ModelMetaclass, LazyBaseHook, LazyImportHook]


class HookMethods(BaseModel):
    """Small model to hold public / private methods."""
    public: dict = {}
    private: dict = {}
    default: dict


class Hooks(BaseModel):
    """Collection of hooks to call. Kept generic to break circular dependency."""
    public: dict[str, GenericHookType] = None
    private: dict[str, GenericHookType] = None
    native: dict[str, GenericHookType] = None
    default: GenericHookType = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class Context(BaseModel):
    # Supplied via command line 
    no_input: Optional[bool] = Field(
        False,
        description="A boolean to suppress any inputs and use defaults while parsing."
    )
    verbose: Optional[bool] = Field(
        False,
        description="A boolean to show internal logs while parsing."
    )

    # Internal data objects 
    input: InputArguments = None
    source: Source = None
    hooks: Hooks = None
    data: Data = None
    path: Paths = None
    key_path: list[Union[str, bytes]] = Field(
        None,
        description="A list of parsed keys in an object / or byte encoded indexes for"
                    " items in an array. Used to track position within a document."
    )
    key_path_block: list[Union[str, bytes]] = Field(
        None,
        description="An indexed version of the key path used within blocks to maintain"
                    " temporary data for rendering. See [docs]()"
    )
    env_: Any = Field(StrictEnvironment(), description="Used internally for rendering.")

    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )


# Note we have a circular dependency between Context having Hooks and BaseHook having 
# Context where we prefer carrying into BaseHook since this is user facing. 
class BaseHook(HookBase):
    """
    Base class that all python hooks extend. 
    """
    hook_type: str = Field(..., description="Name of the hook.")
    context: Context = Field(
        ...,
        description="Context which can be manipulated within the hook.",
    )
    hook_call: HookCallInput = Field(
        ...,
        description="Items from the call of the hook.",
    )

    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )


class DclHookInput(BaseModel):
    """Function input model. Used to validate the raw function input."""
    extends: Union[str, list[str]] | None = Field(
        None,
        description="A string or list of hook types to inherit from. See"
                    " [docs]()."
    )
    # Note: Needs underscore suffix to differentiate from internal exec
    exec_: Any = Field(
        None,
        description="An exec method to run after validating input variables. See"
                    " [docs]().",
        aliases="exec",
    )
    return_: Any = Field(
        None,
        # TODO: Move to macro?
        description="",
        aliases="return",
    )
    type: str | None = Field(
        None,
        # TODO: Move to macro?
        description="For type hooks, the name of the type."
    )
    validators: dict[str, Callable] | None = Field(
        None,
        description="A list of validators. Only used for type hooks. See [docs]()."
    )

    include: list | None = Field(
        None,
        description="A list of fields to include when exporting a model."
    )
    exclude: list | None = Field(
        None,
        description="A list of fields to exclude when exporting a model."
    )

    hook_model_config_: DclHookModelConfig | None = Field(
        None,
        description="Variables to set wrapping pydantic's existing ConfigDict. See"
                    " [docs]().",
        alias="model_config",  # Does not interfere with actual `model_config`
    )



    hook_fields_set_: set = Field(set(), description="Used internally to track fields.")
    hook_fields_: dict = Field(
        {},
        description="Raw version of the hook's fields parsed out as any extra fields in"
                    " validator.")

    @model_validator(mode='before')
    def move_extra(cls, values: dict[str, Any]) -> dict[str, Any]:
        extra: dict[str, Any] = {}
        for field_name in list(values):
            if field_name not in cls.model_fields:
                extra[field_name] = values.pop(field_name)
        values['hook_fields_'] = extra
        return values

    model_config = ConfigDict(
        extra='ignore',
        validate_assignment=True
    )

    def exec(self):
        return self.model_dump(include=self.hook_fields_)

class BaseDclHook(BaseHook):
    """Base model when creating new functions."""
    hook_input: DclHookInput


# HookType = Union[LazyBaseFunction, LazyImportHook, BaseHook]
AnyHookType = Union[
    BaseHook,
    DclHookInput,
    LazyBaseHook,
    LazyImportHook,
]
CompiledHookType = Union[
    BaseHook,
    DclHookInput,
]


class NewHook(BaseHook):
    hook_type: str = 'foo'


nh = NewHook(context=Context(), hook_call=HookCallInput())
d = DclHookInput(hook_type='foo', context=Context(), hook_call=HookCallInput())
h = Hooks()
c = Context()
