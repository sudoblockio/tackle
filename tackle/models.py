import enum
from typing import Any, Optional, Union, ClassVar, Callable, Literal

from pydantic import BaseModel, ConfigDict, Field

from tackle.pydantic.config import DclHookModelConfig


class LazyBaseHook(BaseModel):
    """
    Base class that declarative hooks are derived from and either imported when a
     tackle file is read (by searching in adjacent hooks directory) or on init in local
     providers. Used by jinja extensions and filters.
    """

    hook_name: str
    input_raw: dict = Field(
        ...,
        description="A dict for the lazy function to be parsed at runtime. Serves as a "
        "carrier for the function's schema until it is compiled with "
        "`create_function_model`.",
    )
    is_public: bool = Field(..., description="Public or private.")


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
        alias="cd",
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
        description="A dict to map to inputs for a hook. String inputs rendered by"
        " default but must be references to dicts.",
        render_by_default=True,
    )
    skip_output: bool | None = Field(
        False,
        description="A flag to not set the key. Can also be set in hook definition.",
        render_by_default=True,
    )
    return_: bool | None = Field(
        False,
        description="Flag to indicate whether to stop parsing and return the current"
        " public data.",
        alias="return",
    )
    no_input: bool | None = Field(
        False,
        description="A flag to skip any prompting. Can also be set from command line.",
        render_by_default=True,
    )

    # We'll be accessing all extra fields via __pydantic_fields_set__ instance attribute
    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True,
    )


class HookMethods:
    def __int__(self, public: dict, private: dict, default: dict):
        self.public = public
        self.private = private
        self.default = default


class HookBase(BaseModel):

    __methods__: ClassVar[set[str]]

    __args__: ClassVar[set[tuple[str, str]]] = set()

    __public_methods__: ClassVar[list[str]] = []
    __private_methods__: ClassVar[list[str]] = []
    __is_public__: ClassVar[bool] = False
    __provider_name__: ClassVar[str]

    help: str = Field(
        None,
        description="A string to display when calling with the `help` argument.",
        exclude=True,
    )
    render_by_default: list = Field(
        None,
        description="A list of string fields to wrap with jinja braces and render by "
        "default.",
        exclude=True,
    )
    render_exclude: list = Field(
        None,
        description="A list of field names to not render.",
        exclude=True,
    )
    is_public: bool = Field(
        None,
        description="A boolean if hook is public / callable from outside the provider).",
        exclude=True,
    )
    skip_output: bool = Field(
        False,
        description="A flag to skip the output and not set the key. Can also be set"
        " within a hook call.",
        exclude=True,
    )
    # args: ClassVar[list] = Field(
    #     None,
    #     description="A list of fields map arguments. See [docs]() for details.",
    #     # exclude=True,
    # )

    args: list = Field(
        [],
        description="A list of fields map arguments. See [docs]() for details.",
        exclude=True,
    )
    kwargs: str = Field(
        None,
        description="A field name of type dict to map additional arguments to.",
        exclude=True,
    )


class BaseHook(HookBase):
    """Base class that all python hooks extend."""
    hook_name: ClassVar[str] = None

    __is_python__: ClassVar[bool] = True

    # hook_config: ClassVar[HookConfig] = HookConfig()
    # __public_methods__: ClassVar[list[str]] = []
    # __private_methods__: ClassVar[list[str]] = []
    # __is_public__: ClassVar[bool] = False
    # __provider_name__: ClassVar[str]

    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True,
        validate_assignment=True,
        populate_by_name=True,
        # TODO: Make this dynamic when config is exposed. This is fine for now as there
        #  is no reason to have enum's in raw form.
        use_enum_values=True,
    )


class HookValidatorModes(str, enum.Enum):
    before = 'before'
    after = 'after'
    wrap = 'wrap'


class HookFieldValidatorFieldNames(BaseModel):
    value: str = Field(
        'v',
        description="The name of the value field for validation, the first arg in a "
        "pydantic functional validator.",
    )
    info: str = Field(
        'info',
        description="The name of the info field for validation, the second arg in a "
        "pydantic functional validator.",
    )


class HookFieldValidator(BaseModel):
    field_names: HookFieldValidatorFieldNames = Field(
        default_factory=HookFieldValidatorFieldNames,
        description="The names of fields to inject as variables within the body of "
        "the validator.",
    )
    mode: HookValidatorModes = Field(
        'before',
        description="Whether to run the validator 'before' or 'after' the type is "
        "validated or 'wrap' the validation (ie run it 'before' and "
        "'after'. Follows pydantic's validation logic.",
    )
    body: dict = Field(
        None,
        description="Some data to parse which normally would have some `return` hook "
        "call that would be the validation output.",
    )
    model_config = ConfigDict(
        use_enum_values=True,
        extra='allow',
    )


class DclHookInput(HookBase):
    """Function input model. Used to validate the raw function input."""

    extends: Union[str, list[str]] | None = Field(
        None,
        description="A string or list of hook types to inherit from. See  [docs]().",
    )

    public_methods: dict[str, Callable] = {}
    private_methods: dict[str, Callable] = {}

    # Note: Needs underscore suffix to differentiate from internal exec
    exec_: Any = Field(
        None,
        description="An exec method to run after validating input variables. See"
        " [docs]().",  # TODO
        alias="exec",
    )
    # return_: Any = Field(
    #     None,
    #     # TODO: Move to macro?
    #     description="",
    #     alias="return",
    # )
    # type_: str | None = Field(
    #     None,
    #     alias='type',
    #     description="For type hooks, the name of the type.",
    # )
    validators: dict[str, dict | HookFieldValidator] = Field(
        {},
        description="A list of validators. Only used for type hooks. See [docs]().",
    )
    include: list | None = Field(
        None,
        description="A list of fields to include when exporting a model.",
    )
    exclude: list | None = Field(
        None,
        description="A list of fields to exclude when exporting a model.",
    )
    hook_model_config_: DclHookModelConfig | None = Field(
        None,
        description="Variables to set wrapping pydantic's existing ConfigDict. See"
        " [docs]().",
        alias="model_config",  # Does not interfere with actual `model_config`
    )

    model_config = ConfigDict(
        extra='allow',
        validate_assignment=True,
    )

    # def exec(self):
    #     return self.model_dump(include=self.hook_fields_)


# Set of DclHookInput fields that account for anything with aliases
DCL_HOOK_FIELDS = {
    DclHookInput.model_fields[i].alias
    if DclHookInput.model_fields[i].alias is not None
    else i
    for i in DclHookInput.model_fields.keys()
}

AnyHookType = BaseHook | DclHookInput | LazyBaseHook
GenericHookType = BaseHook | LazyBaseHook
HookDictType = dict[str, AnyHookType]
CompiledHookType = BaseHook | DclHookInput
