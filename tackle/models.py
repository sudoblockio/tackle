import os
import sys
import re
import inspect
import threading
import subprocess
import importlib.machinery
from abc import ABC

from pydantic import (
    BaseModel,
    SecretStr,
    Field,
    Extra,
    validator,
    validate_model,
    ConfigError,
)
from pydantic.main import ModelMetaclass
from pydantic.fields import UndefinedType, ModelField
from jinja2 import Environment, StrictUndefined
from jinja2.ext import Extension
from typing import Any, Union, Optional, Dict, Type, Tuple
import logging
import random
import string

from tackle.utils.paths import listdir_absolute
from tackle.utils.dicts import get_readable_key_path
from tackle.render import wrap_jinja_braces
from tackle.utils.files import read_config_file

logger = logging.getLogger(__name__)


class LazyImportHook(BaseModel):
    """Object to hold hook metadata so that it can be imported only when called."""

    hooks_path: str
    mod_name: str
    provider_name: str
    hook_type: str

    def wrapped_exec(self, **kwargs):
        kwargs['provider_hooks'].import_with_fallback_install(
            mod_name=self.mod_name,
            path=self.hooks_path,
        )
        return kwargs['provider_hooks'][self.hook_type].wrapped_exec()


class ProviderHooks(dict):
    """Dict with hook_types as keys mapped to their corresponding objects."""

    # List to keep track of new functions which need to be updated into the jinja env's
    #  filters so that a hook can be called that way.
    new_functions: list = []

    def __init__(self, *args, **kwargs):
        super(ProviderHooks, self).__init__(*args, **kwargs)
        # https://github.com/robcxyz/tackle-box/issues/43
        # run_id used to make the namespace unique when running multiple runs of tackle
        # as in running batches of tests to prevent duplicate validator import errors
        self._run_id = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(4)
        )
        self.import_native_providers()

    def import_hook_from_path(
        self,
        mod_name: str,
        file_path: str,
    ):
        """Import a single hook from a path."""
        file_split = os.path.basename(file_path).split('.')
        file_base = file_split[0]
        file_extension = file_split[-1]
        # Maintaining cookiecutter support here as it might have a `hooks` dir.
        if file_base in ('pre_gen_project', 'post_gen_project', '__pycache__'):
            return
        if file_extension == 'pyc':
            return
        if file_extension in ('yaml', 'yml'):
            file_contents = read_config_file(file_path)
            for k, v in file_contents.items():
                if re.match(r'^[a-zA-Z0-9\_]*(<\-|<\_)$', k):
                    self[k[:-2]] = LazyBaseFunction(**v)
                    self.new_functions.append(k[:-2])
            return

        if os.path.basename(file_path).split('.')[-1] != "py":
            # Only import python files
            return

        # Use a unique RUN_ID to prevent duplicate validator errors
        # https://github.com/robcxyz/tackle-box/issues/43
        loader = importlib.machinery.SourceFileLoader(
            mod_name + '.hooks.' + file_base[0] + self._run_id, file_path
        )

        module = loader.load_module()

        for k, v in module.__dict__.items():
            if (
                isinstance(v, ModelMetaclass)
                and 'hook_type' in v.__fields__
                and k != 'BaseHook'
                and v.__fields__['hook_type'].default is not None
            ):
                self[v.__fields__['hook_type'].default] = v

    def import_hooks_from_dir(
        self,
        mod_name: str,
        path: str,
        skip_on_error: bool = False,
    ):
        """
        Import hooks from a directory. This is meant to be used by generically pointing to
         a hooks directory and importing all the relevant hooks into the context.
        """
        potential_hooks = listdir_absolute(path)
        for f in potential_hooks:
            if skip_on_error:
                try:
                    self.import_hook_from_path(mod_name, f)
                except (ModuleNotFoundError, ConfigError):
                    logger.debug(f"Skipping importing {f}")
                    continue
            else:
                self.import_hook_from_path(mod_name, f)

    def import_with_fallback_install(
        self, mod_name: str, path: str, skip_on_error: bool = False
    ):
        """
        Import a module and on import error, fallback on requirements file and try to
         import again.
        """
        try:
            self.import_hooks_from_dir(mod_name, path, skip_on_error)
        except ModuleNotFoundError:
            requirements_path = os.path.join(path, '..', 'requirements.txt')
            if os.path.isfile(requirements_path):
                # It is a convention of providers to have a requirements file at the base.
                # Install the contents if there was an import error
                subprocess.check_call(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "--quiet",
                        "--disable-pip-version-check",
                        "-r",
                        requirements_path,
                    ]
                )
            self.import_hooks_from_dir(mod_name, path)

    def import_from_path(self, provider_path: str):
        """Append a provider with a given path."""
        provider_name = os.path.basename(provider_path)
        mod_name = 'tackle.providers.' + provider_name
        hooks_init_path = os.path.join(provider_path, 'hooks', '__init__.py')
        hooks_path = os.path.join(provider_path, 'hooks')

        # If the provider has an __init__.py in the hooks directory, import that
        # to check if there are any hook types declared there.  If there are, store
        # those references so that if the hook type is later called, the hook can
        # then be imported.
        if os.path.isfile(hooks_init_path):
            loader = importlib.machinery.SourceFileLoader(mod_name, hooks_init_path)
            mod = loader.load_module()
            hook_types = getattr(mod, 'hook_types', [])
            for h in hook_types:
                hook = LazyImportHook(
                    hooks_path=hooks_path,
                    mod_name=mod_name,
                    provider_name=provider_name,
                    hook_type=h,
                )
                self[h] = hook

        # This pass will import all the modules and extract hooks
        self.import_with_fallback_install(mod_name, hooks_path, skip_on_error=True)

    @staticmethod
    def get_native_provider_paths():
        """Get a list of paths to the native providers."""
        providers_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'providers'
        )
        native_providers = [
            os.path.join(providers_path, f)
            for f in os.listdir(providers_path)
            if os.path.isdir(os.path.join(providers_path, f)) and f != '__pycache__'
        ]
        return native_providers

    def import_native_providers(self):
        """Iterate through paths and import them."""
        native_provider_paths = self.get_native_provider_paths()
        for i in native_provider_paths:
            self.import_from_path(i)


class PartialModelMetaclass(ModelMetaclass):
    """
    Metaclass to allow partial model initialization.
    See https://github.com/samuelcolvin/pydantic/issues/1223#issuecomment-998160737
    """

    def __new__(
        meta: Type["PartialModelMetaclass"], *args: Any, **kwargs: Any
    ) -> "PartialModelMetaclass":
        try:
            cls = super(PartialModelMetaclass, meta).__new__(meta, *args, **kwargs)
        except Exception as e:
            raise e
        cls_init = cls.__init__
        # Because the class will be modified temporarily, need to lock __init__
        init_lock = threading.Lock()
        # To preserve identical hashes of temporary nested partial models,
        # only one instance of each temporary partial class can exist
        temporary_partial_classes: Dict[str, ModelMetaclass] = {}

        def __init__(self: BaseModel, *args: Any, **kwargs: Any) -> None:
            with init_lock:
                fields = self.__class__.__fields__
                fields_map: Dict[ModelField, Tuple[Any, bool]] = {}

                def optionalize(
                    fields: Dict[str, ModelField], *, restore: bool = False
                ) -> None:
                    for _, field in fields.items():
                        if not restore:
                            assert not isinstance(field.required, UndefinedType)
                            fields_map[field] = (field.type_, field.required)
                            field.required = False
                            if (
                                inspect.isclass(field.type_)
                                and issubclass(field.type_, BaseModel)
                                and not field.type_.__name__.startswith(
                                    "TemporaryPartial"
                                )
                            ):
                                # Assign a temporary type to optionalize to avoid
                                # modifying *other* classes
                                class_name = f"TemporaryPartial{field.type_.__name__}"
                                if class_name in temporary_partial_classes:
                                    field.type_ = temporary_partial_classes[class_name]
                                else:
                                    field.type_ = ModelMetaclass(
                                        class_name,
                                        (field.type_,),
                                        {},
                                    )
                                    temporary_partial_classes[class_name] = field.type_
                                optionalize(field.type_.__fields__)
                                # After replacing the field type, regenerate validators
                                field.populate_validators()
                        else:
                            # No need to recursively de-optionalize once original types
                            # are restored
                            field.type_, field.required = fields_map[field]

                # Make fields and fields of nested model types optional
                optionalize(fields)
                # Transform kwargs that are PartialModels to their dict() forms. This
                # will exclude `None` (see below) from the dictionary used to construct
                # the temporarily-partial model field, avoiding ValidationErrors of
                # type type_error.none.not_allowed.
                for kwarg, value in kwargs.items():
                    if value.__class__.__class__ is PartialModelMetaclass:
                        kwargs[kwarg] = value.dict()
                # Validation is performed in __init__, for which all fields are now optional
                if args:
                    for i, v in enumerate(args):
                        kwargs[self.args[i]] = v
                # cls is always initialized with kwargs not args.
                try:
                    cls_init(self, **kwargs)
                except Exception as e:
                    raise e
                # Restore requiredness
                optionalize(fields, restore=True)

        setattr(cls, "__init__", __init__)

        # Exclude unset (`None`) from dict(), which isn't allowed in the schema
        # but will be the default for non-required fields. This enables
        # PartialModel(**PartialModel().dict()) to work correctly.
        cls_dict = cls.dict

        def dict_exclude_unset(
            self: BaseModel, *args: Any, exclude_unset: bool = None, **kwargs: Any
        ) -> Dict[str, Any]:
            return cls_dict(self, *args, **kwargs, exclude_unset=True)

        cls.dict = dict_exclude_unset

        return cls


class StrictEnvironment(Environment):
    """Create strict Jinja2 environment.

    Jinja2 environment will raise error on undefined variable in template-
    rendering context.
    """

    def __init__(self, provider_hooks: dict, **kwargs):
        super(StrictEnvironment, self).__init__(undefined=StrictUndefined, **kwargs)
        # Import filters into environment
        for k, v in provider_hooks.items():
            if isinstance(v, LazyImportHook):
                self.filters[k] = v.wrapped_exec
            elif isinstance(v, LazyBaseFunction):
                self.filters[k] = v.wrapped_exec
            else:
                # Filters don't receive any context (public_context, etc)
                self.filters[k] = v().wrapped_exec


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
    provider_hooks: ProviderHooks = None

    calling_directory: str = None
    calling_file: str = None
    current_file: str = None

    env_: Any = None


class Context(BaseContext):
    """The main object that is being modified by parsing."""

    # Source
    password: SecretStr = None
    directory: str = None
    find_in_parent: bool = False
    input_string: str = None
    input_dir: str = None
    input_file: str = None

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
        # Allows for passing the providers between tackle runtimes
        if self.provider_hooks is None:
            self.provider_hooks = ProviderHooks()

        if self.env_ is None:
            self.env_ = StrictEnvironment(self.provider_hooks)

        if self.calling_directory is None:
            # Can be carried over from another context. Should only be initialized when
            # called from CLI.
            self.calling_directory = os.path.abspath(os.path.curdir)


class BaseHook(BaseContext, Extension, metaclass=PartialModelMetaclass):
    """
    Base hook class from which all other hooks inherit from to be discovered. There are
    a number of reserved keys that are used for logic such as `if` and `for` that are
    aliased to `if_` and `for_` to not collide with python reserved key words.
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

    # Placeholder until help can be fully worked out
    help: str = None

    # Flag for whether being called directly (True) or by a jinja extension (False)
    is_hook_call: bool = False
    skip_import: bool = False
    hooks_path: str = None

    env_: Any = None

    args: list = []

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

    def exec(self) -> Any:
        raise NotImplementedError("Every hook needs an exec method.")

    # https://github.com/samuelcolvin/pydantic/issues/1864#issuecomment-679044432
    def validate(self, **kwargs):
        """Manual validation with mapping back aliases as they will be remapped."""
        # For some reason changes here apply to all instances of a class and so if a
        # hook is reused, it will fail because the special aliased fields are already
        # remapped. This is a hack.
        if 'if_' in self.__dict__:
            for k, v in self.Config.fields.items():
                self.__dict__[v] = self.__dict__[k]
                self.__dict__.pop(k)
        *_, validation_error = validate_model(self.__class__, self.__dict__)
        if validation_error:
            raise validation_error

    def wrapped_exec(self, *args, **kwargs):
        # Map args / kwargs
        if args:
            num_args = len(args)
            for i, v in enumerate(self.args):
                if i >= num_args:
                    break
                setattr(self, v, args[i])
            if len(args) > len(self.args):
                raise Exception(
                    f"Too many arguments in {get_readable_key_path(self.key_path)}"
                )
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.validate()
        return self.exec()


class FunctionInput(BaseModel):
    """Function input model."""

    exec_: Any = Field(None)
    return_: Union[str, list] = Field(None)

    args: list = None
    render_exclude: list = None
    validators: dict = None
    methods: dict = None
    public: bool = None
    extends: str = None

    class Config:
        extra = 'ignore'


class BaseFunction(BaseHook, FunctionInput, ABC):
    """Function input model."""

    function_fields: list


class LazyBaseFunction(BaseFunction, Extension, metaclass=PartialModelMetaclass):
    """
    Base function that declarative hooks are derived from and either imported when a
     tackle file is read (by searching in adjacent hooks directory) on init in local
     providers. Used by jinja extensions and filters.
    """

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.allow
        # TODO: Figure this out as it is needed in the combined jinja hook wrapped exec
        #  logic... In this case we already have it serialized?
        # Not sure what is going on here
        fields = {
            'if_': 'if_',
            'else_': 'else_',
            'for_': 'for_',
            'try_': 'try_',
            'except_': 'except_',
        }
