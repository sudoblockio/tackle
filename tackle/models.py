import os
import logging
import subprocess
import sys
import importlib.machinery
from pydantic import BaseModel, SecretStr, Field, Extra, validator, ConfigError
from pydantic.main import ModelMetaclass
from pydantic.fields import UndefinedType, ModelField
from jinja2.ext import Extension
from typing import Any, Union, Optional, Dict, Type, Tuple
import threading
import inspect

from tackle.utils.paths import work_in
from tackle.utils.dicts import get_readable_key_path
from tackle.render import wrap_jinja_braces
from tackle.utils.paths import listdir_absolute


logger = logging.getLogger(__name__)


class PartialModelMetaclass(ModelMetaclass):
    def __new__(
        meta: Type["PartialModelMetaclass"], *args: Any, **kwargs: Any
    ) -> "PartialModelMetaclass":
        """See https://github.com/samuelcolvin/pydantic/issues/1223#issuecomment-998160737"""
        cls = super(PartialModelMetaclass, meta).__new__(meta, *args, **kwargs)
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
                cls_init(self, *args, **kwargs)
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


class Context(BaseModel):
    """The main object that is being modified by parsing."""

    # Mode
    no_input: bool = False
    verbose: bool = False

    # Source
    password: SecretStr = None
    directory: str = None
    find_in_parent: bool = False

    # Inputs
    input_string: str = None
    # input_dir: Path = None
    input_dir: str = None

    input_file: str = None
    checkout: str = Field(
        None,
        description="For inputs referencing remote repos, refers to a branch or tag.",
    )
    existing_context: dict = {}
    overwrite_inputs: Union[dict, str] = None

    input_dict: dict = {}
    output_dict: dict = {}
    keys_to_remove: list = []

    # Internal
    key_path: list = []
    # providers: ProviderList = None
    # providers: dict = None

    provider_hooks: dict = None

    calling_directory: str = None
    calling_file: str = None
    env: Any = None

    global_args: list = None
    global_kwargs: dict = None
    global_flags: list = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Allows for passing the providers between tackle runtimes
        if self.provider_hooks is None:
            self.provider_hooks = {}
            import_native_providers(self.provider_hooks)

        # if self.providers is None:
        #     # Native and settings.extra_providers initialized
        #     self.providers = {}
        # from tackle.import_dict import
        # self.providers = ProviderList()

        if self.calling_directory is None:
            # Can be carried over from another context. Should only be initialized when
            # called from CLI.
            self.calling_directory = os.path.abspath(os.path.curdir)


class BaseHook(BaseModel, Extension, metaclass=PartialModelMetaclass):
    """
    Base hook class from which all other hooks inherit from to be discovered. There are
    a number of reserved keys that are used for logic such as `if` and `for` that are
    aliased to `if_` and `for_` to not collide with python reserved key words. We also
    append underscores to

    """

    hook_type: str = Field(..., description="Name of the hook.")

    # TODO: Serialize the access modifier earlier in parsing - Could store the arrow in
    #  key_path as boolean. Would have big changes to tackle.utils.dicts
    # access_modifier: Literal['public', 'private'] = None

    if_: Union[str, bool] = Field(None, render_by_default=True)
    else_: Any = Field(None, render_by_default=True)
    for_: Union[str, list] = Field(None, render_by_default=True)
    reverse: Union[str, bool] = Field(None, render_by_default=True)
    try_: Union[str, bool] = Field(None, render_by_default=True)

    callback: str = None
    chdir: Optional[str] = Field(None, description="Name of the hook.")
    merge: Union[bool, str] = None
    confirm: Optional[Any] = None

    # context parameters - must be same type as context
    input_dict: Union[dict, list] = None
    output_dict: Union[dict, list] = {}
    existing_context: dict = None
    no_input: bool = None
    calling_directory: str = None
    calling_file: str = None
    verbose: bool = False

    # providers: ProviderList = None
    key_path: list = None

    # Placeholder until help can be fully worked out
    help: str = None

    # Flag for whether being called directly (True) or by a jinja extension (False)
    is_hook_call: bool = False
    skip_import: bool = False
    hooks_path: str = None

    # For tackle hook that needs to pass this expensive to instantiate object through
    provider_hooks: dict = None

    _args: list = []
    _kwargs: dict = {}
    _flags: list = []
    # Fields that should not be rendered by default
    _render_exclude_default: set = {'input_dict', 'output_dict', 'hook_type'}
    _render_exclude: set = {}
    _render_by_default: list = []

    # Used when rendering docs
    _doc_tags: list = []
    # For linking issues in the docs so others can potentially contribute
    _issue_numbers: list = []
    # Additional callout sections to be included at the top of the docs
    _notes: list = []
    # Allow hooks to be sorted in the docs
    _docs_order: int = 10  # Arbitrary high number so hooks can be sorted high or low
    # Parameterized return type description for docs
    _return_description: str = None

    environment: Any = None

    @validator('if_', 'else_', 'reverse', 'for_', 'merge')
    def wrap_bool_if_string(cls, v):
        return wrap_jinja_braces(v)

    # Per https://github.com/samuelcolvin/pydantic/issues/1577
    # See below
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
            # 'while_': 'while',
        }
        # Per https://github.com/samuelcolvin/pydantic/issues/1577
        # This is an issue until pydantic 1.9 is released and items can be set with
        # properties which will override the internal __setattr__ method that
        # disregards aliased fields
        alias_to_fields = {v: k for k, v in fields.items()}

    # def __init__(self, **data: Any):
    #     super().__init__(**data)
    #     if not self.is_hook_call and 'environment' in data:
    #         def f(obj):
    #             return obj
    #         data['environment'].filters[self.hook_type] = f

    def __init__(self, environment=None, *args: Any, **data: Any):
        # TODO: Checkout https://github.com/samuelcolvin/pydantic/issues/1223#issuecomment-998160737
        #  to support partial instantiation. Would need to modify base class
        super().__init__(environment=environment, **data)

        if not self.is_hook_call and self.environment:
            environment.globals[self.hook_type] = self.wrapped_exec
            # setattr(self.environment.globals, self.hook_type, self.execute)

    def execute(self) -> Any:
        raise NotImplementedError("Every hook needs an execute method.")

    def wrapped_exec(self, *args, **kwargs):
        # Map args / kwargs
        for i, v in enumerate(self._args):
            setattr(self, v, args[i])
        if len(args) > len(self._args):
            raise Exception(
                f"Too many arguments in {get_readable_key_path(self.key_path)}"
            )
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self.execute()

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


class LazyImportHook(BaseModel):
    hooks_path: str
    mod_name: str
    provider_name: str
    hook_type: str

    # def import_hook_to_environment(self, environment):
    #     environment.globals[self.hook_type] = self.execute


def import_hook_from_path(
    provider_hook_dict: dict,
    mod_name: str,
    file_path: str,
):
    """Import a single hook from a path."""
    # Maintaining cookiecutter support here as it might have a `hooks` dir.
    excluded_file_names = ['pre_gen_project', 'post_gen_project', '__pycache__']
    excluded_file_extensions = ['pyc']

    file_base = os.path.basename(file_path).split('.')
    if file_base[0] in excluded_file_names:
        return
    if file_base[-1] in excluded_file_extensions:
        return

    if os.path.basename(file_path).split('.')[-1] != "py":
        # Only import python files
        return

    loader = importlib.machinery.SourceFileLoader(
        mod_name + '.hooks.' + file_base[0], file_path
    )

    module = loader.load_module()

    for k, v in module.__dict__.items():
        if not isinstance(v, ModelMetaclass):
            continue
        if issubclass(v, BaseHook) and v != BaseHook:
            provider_hook_dict[v.__fields__['hook_type'].default] = v


def import_hooks_from_dir(
    provider_hook_dict: dict,
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
                import_hook_from_path(provider_hook_dict, mod_name, f)
            except (ModuleNotFoundError, ConfigError):
                logger.debug(f"Skipping importing {f}")
                continue
        else:
            import_hook_from_path(provider_hook_dict, mod_name, f)


def import_with_fallback_install(
    provider_hook_dict: dict, mod_name: str, path: str, skip_on_error: bool = False
):
    """
    Import a module and on import error, fallback on requirements file and try to
     import again.
    """
    try:
        import_hooks_from_dir(provider_hook_dict, mod_name, path, skip_on_error)
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
        import_hooks_from_dir(provider_hook_dict, mod_name, path)


def import_from_path(provider_hook_dict: dict, provider_path: str):
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
        # mod = import_module_from_path(mod_name, hooks_init_path)
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
            provider_hook_dict[h] = hook

    # This pass will import all the modules and extract hooks
    import_with_fallback_install(
        provider_hook_dict, mod_name, hooks_path, skip_on_error=True
    )


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


def import_native_providers(provider_hook_dict: dict) -> dict:
    """Iterate through paths and import them."""
    native_provider_paths = get_native_provider_paths()
    for i in native_provider_paths:
        import_from_path(provider_hook_dict, i)

    return provider_hook_dict
