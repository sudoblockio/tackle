import os
import random
import string
from abc import ABC
from pydantic import (
    BaseModel,
    SecretStr,
    Field,
    Extra,
    validator,
)
from pydantic.main import ModelMetaclass
from jinja2 import Environment, StrictUndefined
from jinja2.ext import Extension
from typing import Any, Union, Optional, Callable

from tackle.hooks import import_native_providers, import_hooks_from_dir
from tackle.utils.render import wrap_jinja_braces
from tackle.exceptions import TooManyTemplateArgsException


class StrictEnvironment(Environment):
    """Create strict Jinja2 environment.

    Jinja2 environment will raise error on undefined variable in template-
    rendering context.
    """

    def __init__(self, **kwargs):
        super(StrictEnvironment, self).__init__(undefined=StrictUndefined, **kwargs)
        # TODO: Add imports for jinja hook filters


class BaseContext(BaseModel):
    """Shared items that are passed between hook calls and the main context."""

    no_input: bool = False
    verbose: bool = False

    input_context: Union[dict, list] = None
    public_context: Union[dict, list] = None
    private_context: Union[dict, list] = None
    temporary_context: Union[dict, list] = None
    existing_context: dict = {}

    key_path: list = []
    key_path_block: list = []

    # public_hooks: dict = {}
    public_hooks: dict = None
    private_hooks: dict = None
    default_hook: Any = Field(None, exclude=True)

    calling_directory: str = None
    calling_file: str = None
    current_file: str = None

    env_: Any = None

    class Config:
        smart_union = True

    # TODO: RM after dealing with namespace issue for validators
    # https://github.com/robcxyz/tackle/issues/43
    run_id: str = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.run_id is None:
            self.run_id: str = ''.join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(4)
            )


class Context(BaseContext):
    """The main object that is being modified by parsing."""

    # Source
    password: SecretStr = None
    directory: str = None
    find_in_parent: bool = False
    input_string: str = None
    input_dir: str = None
    input_file: str = None
    override_context: Union[str, dict] = Field(
        None, description="A str for a file or dict to override inputs with."
    )

    context_functions: list = None

    hook_dirs: list = Field(
        None, description="A list of additional directories to import hooks."
    )

    latest: bool = False
    # TODO: Change to version?
    checkout: str = Field(
        None,
        description="For inputs referencing remote repos, refers to a branch or tag.",
    )

    global_args: list = None
    global_kwargs: dict = None
    global_flags: list = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.latest:
            self.checkout = 'latest'

        # Allows for passing the providers between tackle runtimes
        if self.private_hooks is None:
            self.private_hooks = {}
            import_native_providers(self)

        if self.public_hooks is None:
            self.public_hooks = {}

        if self.hook_dirs is not None:
            for i in self.hook_dirs:
                import_hooks_from_dir(context=self, mod_name=i, path=i)

        if self.env_ is None:
            self.env_ = StrictEnvironment()

        if self.calling_directory is None:
            # Can be carried over from another context. Should only be initialized when
            # called from CLI.
            self.calling_directory = os.path.abspath(os.path.curdir)


class BaseHook(BaseContext, Extension):
    """
    Base hook class from which all other hooks inherit from to be discovered. There are
    a number of reserved keys that are used for logic such as `if` and `for` that are
    aliased to `if_` and `for_` to not collide with python reserved keywords.
    """

    hook_type: str = Field(..., description="Name of the hook.")

    if_: Union[str, bool] = Field(None, render_by_default=True)
    when: Union[str, bool] = Field(None, render_by_default=True)
    else_: Any = Field(None)
    for_: Union[str, list] = Field(None, render_by_default=True)
    reverse: Union[str, bool] = Field(None, render_by_default=True)
    try_: Union[str, bool] = Field(None, render_by_default=True)
    except_: Any = Field(None, render_by_default=True)
    chdir: Optional[str] = Field(None, description="Name of the hook.")
    merge: Union[bool, str] = None
    confirm: Optional[Any] = None

    # Flag for whether being called directly (True) or by a jinja extension (False)
    is_hook_call: bool = False
    skip_import: bool = False
    hooks_path: str = None
    is_public: bool = False

    env_: Any = None

    args: list = []
    kwargs: Union[str, dict] = None

    skip_output: bool = False
    # Fields that should not be rendered by default
    _render_exclude_default: set = {
        'input_context',
        'public_context',
        'hook_type',
        'else',
    }
    _render_exclude: set = {}
    _render_by_default: list = []

    # Used when rendering docs
    _doc_tags: list = []
    # For linking issues in the docs so others can potentially contribute
    _issue_numbers: list = []  # TODO: Implement this
    # Additional callout sections to be included at the top of the docs
    _notes: list = []
    # Allow hooks to be sorted in the docs
    _docs_order: int = 10  # Arbitrary high number so hooks can be sorted high or low
    # Parameterized return type description for docs
    _return_description: str = None
    # Flag for skipping creating the docs for
    _wip: bool = False

    @validator('if_', 'reverse', 'for_', 'merge')
    def wrap_bool_if_string(cls, v):
        return wrap_jinja_braces(v)

    # Per https://github.com/samuelcolvin/pydantic/issues/1577
    def __setattr__(self, key, val):
        """Override method to alias input fields."""
        if key in self.__config__.alias_to_fields:
            key = self.__config__.alias_to_fields[key]
        super().__setattr__(key, val)

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.forbid
        validate_assignment = True
        fields = {
            'if_': 'if',
            'else_': 'else',
            'for_': 'for',
            'try_': 'try',
            'except_': 'except',
        }
        # Per https://github.com/samuelcolvin/pydantic/issues/1577
        # This is an issue until pydantic 1.9 is released and items can be set with
        # properties which will override the internal __setattr__ method that
        # disregards aliased fields
        alias_to_fields = {v: k for k, v in fields.items()}

    # TODO: RM?
    def exec(self) -> Any:
        raise NotImplementedError("Every hook needs an exec method.")


class FunctionInput(BaseModel):
    """Function input model. Used to validate the raw function input."""

    exec_: Any = Field(None)
    return_: Union[str, list] = Field(None)

    args: list = None
    kwargs: str = None

    render_exclude: list = None
    validators: dict = None
    methods: dict = None
    public: bool = None
    extends: str = None
    help: str = None

    class Config:
        extra = 'ignore'
        validate_on_assignment = True


class BaseFunction(BaseHook, FunctionInput, ABC):
    """Base model when creating new functions."""


class JinjaHook(BaseModel):
    """
    Model for jinja hooks. Is instantiated in render.py while rendering from unknown
    variables.
    """

    hook: ModelMetaclass
    context: BaseContext

    class Config:
        # TODO: Had to add this to get `make test` to run.
        #  https://github.com/robcxyz/tackle/issues/90
        arbitrary_types_allowed = True

    def wrapped_exec(self, *args, **kwargs):
        # Map args / kwargs when called via a jinja global
        from tackle.parser import evaluate_args

        args_list = list(args)
        for i in args_list:
            if isinstance(i, StrictUndefined):
                raise TooManyTemplateArgsException(
                    "Too many arguments supplied to hook call", context=self.context
                )
        evaluate_args(
            args=args_list, hook_dict=kwargs, Hook=self.hook, context=self.context
        )
        # Can't simply do self.hook(**kwargs, **self.context.dict()) because the
        #  references might not be copied over properly.
        output = self.hook(
            **kwargs,
            input_context=self.context.input_context,
            public_context=self.context.public_context,
            existing_context=self.context.existing_context,
            no_input=self.context.no_input,
            calling_directory=self.context.calling_directory,
            calling_file=self.context.calling_file,
            private_hooks=self.context.private_hooks,
            public_hooks=self.context.public_hooks,
            key_path=self.context.key_path,
            verbose=self.context.verbose,
        ).exec()
        return output

    def set_method(self, key: str, method: Callable):
        """
        Method to attach method attributes onto wrapped_exec method so that function
        can be called from jinja globals. For instance JinjaHook().wrapped_exec will be
        put into jinja.environment.globals which might have a method itself such as
        JinjaHook().wrapped_exec.JinjaHook().wrapped_exec.another_method. This can't
        be done directly with setattr against JinjaHook().wrapped_exec. Inspired by
        https://stackoverflow.com/a/20306101/12642712
        """
        setattr(JinjaHook.wrapped_exec, key, method)
