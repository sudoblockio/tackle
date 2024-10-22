import importlib
import logging
import os
import subprocess
import sys
from functools import lru_cache
from typing import Any, Callable

from pydantic import PydanticUserError, ValidationError
from pydantic._internal._model_construction import ModelMetaclass  # noqa
from pydantic_core import PydanticUndefined

from tackle import exceptions
from tackle.context import Context, Data
from tackle.models import BaseHook, GenericHookType
from tackle.settings import settings
from tackle.utils.files import read_config_file
from tackle.utils.prompts import confirm_prompt

logger = logging.getLogger(__name__)


class PyImportContext:

    key = '__py_import_context'
    def __init__(self):
        self.public_hook_methods: dict[str, list[str]] = {}
        self.private_hook_methods: dict[str, list[str]] = {}


def get_module_from_path(
    context: 'Context',
    module_name: str,
    file_path: str,
):
    """Given a path to a python file, import all the modules."""
    loader = importlib.machinery.SourceFileLoader(module_name, path=file_path)
    if sys.version_info.minor < 10:
        mod = loader.load_module()
    else:
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod

        # Set a temporary key to hold imported methods - to be accessed later
        # TODO: This is going to be replaced with metaclass
        mod.__dict__[PyImportContext.key] = PyImportContext()

        # Add dirname to path to support imports between hooks
        module_dir = os.path.dirname(os.path.abspath(file_path))
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)

        try:
            loader.exec_module(mod)
        except (ValidationError, PydanticUserError) as e:
            raise exceptions.TackleHookImportException(
                e.__str__(), context=context, file=file_path
            )
    return mod


def is_base_hook_subclass(key: str, value: Any) -> bool:
    """
    When importing python hooks from a file, return true if the object is a subclass of
     BaseHook, meaning it is a hook.
    """
    return (
        not key.startswith('_')
        and isinstance(value, ModelMetaclass)
        and issubclass(value, BaseHook)
        and key != 'BaseHook'
    )


def import_python_hooks_from_file(
    context: 'Context',
    module_name: str,
    file_path: str,
):
    """Import python public and private hooks from a file."""
    mod = get_module_from_path(
        context=context,
        module_name=module_name,
        file_path=file_path,
    )

    # Remove the key which the methods were loaded into
    module_import_context: PyImportContext = mod.__dict__.pop(PyImportContext.key)
    public_hook_methods = module_import_context.public_hook_methods
    private_hook_methods = module_import_context.private_hook_methods

    # Loop through all the module items and add the hooks
    for k, v in mod.__dict__.items():
        if not is_base_hook_subclass(key=k, value=v):
            continue  # Skip all non-hooks
        if v.hook_name is None:
            # The `hook_name` field was not specified so just using the class name
            v.hook_name = k
        if not isinstance(v.hook_name, str):
            raise exceptions.MalformedHookDefinitionException(
                f"The python hook defined in class=`{k}` does not "
                f"have a hook_name field defined. Please add one looking like "
                f"`hook_name: str = 'your_hook_name'`",
                context=context,
                hook_name=k,
            )

        # TODO: Add when fixing third_party imports
        # v.__provider_name = provider_name
        hook_name = v.hook_name
        hook_class_name = v.__qualname__
        if v.__is_public__:
            if hook_class_name in public_hook_methods:
                v.__public_methods__ = public_hook_methods[hook_class_name]
            context.hooks.public[hook_name] = v
        else:
            if hook_class_name in private_hook_methods:
                v.__private_methods__ = private_hook_methods[hook_class_name]
            if hook_class_name in public_hook_methods:
                v.__public_methods__ = public_hook_methods[hook_class_name]
            context.hooks.private[hook_name] = v


def import_declarative_hooks_from_file(
    context: 'Context',
    file_path: str,
    file_extension: str = None,
) -> object:
    """Import all the declarative hooks from a directory."""
    from tackle.parser import parse_context
    from tackle.factory import new_data

    file_contents = read_config_file(file=file_path, file_extension=file_extension)
    if file_contents is None:
        logger.debug(f"Skipping importing {file_path} as the context is empty.")
        return
    # Temporarily hold the data in another var to parse the file contents
    old_data = context.data
    context.data = None
    context.data = new_data(context=context, raw_input=file_contents)
    parse_context(context=context, call_hooks=False)
    # Bring the data back
    context.data = old_data


def import_hooks_from_file(
    context: 'Context',
    provider_name: str,
    file_path: str,
):
    """
    Import either public or private hooks from a python file or declarative hook from a
     document (ie json / yaml).
    """
    directory, filename = os.path.split(file_path)
    file_base, file_extension = os.path.splitext(filename)
    file_extension = file_extension[1:]

    if file_extension in ('', 'pyc'):
        return
    if file_base in ('pre_gen_project', 'post_gen_project', '__pycache__'):
        # Maintaining cookiecutter support here as it might have a `hooks` dir.
        return
    elif file_extension in ('yaml', 'yml', 'json', 'toml'):
        # We are trying to import dcl hooks
        import_declarative_hooks_from_file(
            context=context,
            file_path=file_path,
            file_extension=file_extension,
        )
    elif file_extension == "py":
        module_name = provider_name + '.hooks.' + file_base
        import_python_hooks_from_file(
            context=context,
            module_name=module_name,
            file_path=file_path,
        )


def import_hooks_from_hooks_directory(
    context: 'Context',
    provider_name: str,
    hooks_directory: str,
):
    """Import all the hooks in all the files from a directory (`hooks`/`.hooks` dir)."""
    for file in os.scandir(hooks_directory):
        import_hooks_from_file(
            context=context,
            provider_name=provider_name,
            file_path=file.path,
        )


def import_native_hooks_from_directory(
    context: 'Context',
    provider_name: str,
    hooks_directory: str,
    native_hooks: dict[str, 'GenericHookType'],
) -> dict[str, 'GenericHookType']:
    """
    Native hooks are all defined in python so this function only imports python hooks
     from a native provider (ie tackle/providers dir).
    """
    for file in os.scandir(hooks_directory):
        directory, filename = os.path.split(file.path)
        file_base, file_extension = os.path.splitext(filename)

        if file_extension == ".py":
            module_name = 'providers.' + provider_name + '.hooks.' + file_base
            mod = get_module_from_path(
                context=context,
                module_name=module_name,
                file_path=file.path,
            )
            # Loop through all the module items and add the hooks
            for k, v in mod.__dict__.items():
                if is_base_hook_subclass(key=k, value=v):
                    v.__provider_name = provider_name
                    native_hooks[v.hook_name] = v

    return native_hooks


# Cache the result since this will never change between tackle executions. In tests,
# is a session scoped patch.
@lru_cache
def import_native_providers() -> dict[str, 'GenericHookType']:
    """
    Import the native providers. First qualifies if we are running locally (ie the
     `local_install` setting is active in which case we need to manually import all the
      native provides. Otherwise, just use the cached native providers as we would under
      normal runs. Importing providers adds about .7 seconds each time we run tackle.
    """
    # Making empty context so the function is cachable
    context = Context()
    native_hooks = {}

    native_providers_directory = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'providers'
    )
    if settings.local_install:
        for i in os.scandir(native_providers_directory):
            if i.is_dir() and i.name != '__pycache__':
                import_native_hooks_from_directory(
                    context=context,
                    hooks_directory=os.path.join(i.path, 'hooks'),
                    provider_name=i.name,
                    native_hooks=native_hooks,
                )
        return native_hooks
    else:
        # This is where we want to implement a native hook cache which could speed up
        # imports by a whopping .2 seconds or so. Replacing context from pydantic to
        # dataclasses makes this a low priority.
        raise NotImplementedError


def install_requirements_file(requirements_path: str):
    """Shell process to call pip and install a requirements file."""
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


def install_reqs_with_prompt(
    context: 'Context',
    provider_name: str,
    requirements_path: str,
):
    """Checks settings and then potentially prompts user for installing requirements."""
    if context.no_input or not settings.prompt_for_installs:
        install_requirements_file(requirements_path=requirements_path)
    else:
        requirements = []
        with open(requirements_path, 'r') as file:
            for line in file:
                line = line.strip()  # remove trailing and leading white space
                if line:  # skip empty lines
                    if line.startswith('#'):  # skip comments
                        continue
                    # remove version and comments
                    requirement = line.split('==')[0].split('#')[0].strip()
                    requirements.append(requirement)
        install_ok = confirm_prompt(
            f"The provider {provider_name} has some requirements including"
            f" {' '.join(requirements)}. Ok to install?"
        )
        if install_ok:
            install_requirements_file(requirements_path=requirements_path)
        else:
            logger.info(
                f"Did not install requirement for provider {provider_name}."
                f" Exiting..."
            )
            sys.exit(0)


def fallback_install_then_import(
    context: 'Context',
    provider_name: str,
    hooks_directory: str,
):
    """
    If there is a module not found error, we try to install the requirements before
     attempting to import again.
    """
    # We want to make this relative to the hooks directory as it is detected earlier
    # ie (hooks vs .hooks or specified)
    requirements_path = os.path.join(hooks_directory, '..', 'requirements.txt')
    if os.path.isfile(requirements_path):
        # It is a convention of providers to have a requirements file at the base.
        # Install the contents if there was an import error
        install_reqs_with_prompt(
            context=context,
            provider_name=provider_name,
            requirements_path=requirements_path,
        )
    import_hooks_from_hooks_directory(
        context=context,
        provider_name=provider_name,
        hooks_directory=hooks_directory,
    )


def import_with_fallback_install(
    context: 'Context',
    provider_name: str,
    hooks_directory: str,
):
    """
    Import a module and on import error, fallback on requirements file and try to
     import again.
    """
    try:
        # TODO: Implement looping outside of the try
        import_hooks_from_hooks_directory(
            context=context,
            provider_name=provider_name,
            hooks_directory=hooks_directory,
        )
    except ModuleNotFoundError:
        fallback_install_then_import(
            context=context,
            provider_name=provider_name,
            hooks_directory=hooks_directory,
        )
