import os
import re
import sys
import importlib
import logging
from pydantic import BaseModel, Field, ConfigError
from pydantic.main import ModelMetaclass
import subprocess
from typing import TYPE_CHECKING

# TODO: RM after dealing with namespace issue for validators
# https://github.com/robcxyz/tackle/issues/43
# import random
# import string

from tackle.utils.paths import listdir_absolute
from tackle.utils.files import read_config_file

if TYPE_CHECKING:
    from tackle.models import Context

logger = logging.getLogger(__name__)


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
            path=self.hooks_path,
        )
        return kwargs['provider_hooks'][self.hook_type].wrapped_exec()


class LazyBaseFunction(BaseModel):
    """
    Base function that declarative hooks are derived from and either imported when a
     tackle file is read (by searching in adjacent hooks directory) or on init in local
     providers. Used by jinja extensions and filters.
    """

    function_dict: dict = Field(
        ...,
        description="A dict for the lazy function to be parsed at runtime. Serves as a "
        "carrier for the function's schema until it is compiled with "
        "`create_function_model`.",
    )
    function_fields: list = Field(
        None,
        description="List of fields used to 1, enrich functions without exec method, "
        "and 2, inherit base attributes into methods. Basically a helper.",
    )


def import_from_path(
    context: 'Context',
    provider_path: str,
    hooks_dir_name: str = None,
    skip_on_error: bool = True,
):
    """Append a provider with a given path."""
    # Look for `.hooks` or `hooks` dir
    if hooks_dir_name is None:
        provider_contents = os.listdir(provider_path)
        if '.hooks' in provider_contents:
            hooks_dir_name = '.hooks'
        elif 'hooks' in provider_contents:
            hooks_dir_name = 'hooks'
        else:
            return

    provider_name = os.path.basename(provider_path)
    mod_name = 'tackle.providers.' + provider_name
    hooks_init_path = os.path.join(provider_path, hooks_dir_name, '__init__.py')
    hooks_path = os.path.join(provider_path, hooks_dir_name)

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

            if hook.is_public:
                context.public_hooks[h] = hook
            else:
                context.private_hooks[h] = hook

    # This pass will import all the modules and extract hooks
    import_with_fallback_install(
        context=context, mod_name=mod_name, path=hooks_path, skip_on_error=skip_on_error
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


def import_native_providers(context: 'Context'):
    """Iterate through paths and import them."""
    native_provider_paths = get_native_provider_paths()
    for i in native_provider_paths:
        import_from_path(context, i, hooks_dir_name='hooks')


def import_hook_from_path(
    context: 'Context',
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
        # TODO: Turn this into a parser so that declarative hooks can be imported.
        #  Difference is now that we have access modifiers for hooks where

        # Import declarative hooks
        file_contents = read_config_file(file_path)
        if file_contents is None:
            if context.verbose:
                print(f"Skipping importing {file_path} as the context is empty.")
            return
        for k, v in file_contents.items():
            if re.match(r'^[a-zA-Z0-9\_]*(<\-)$', k):
                hook_type = k[:-2]
                # context.public_context[hook_type] = LazyBaseFunction(
                #     function_dict=v,
                #     # function_fields=[],
                # )
                context.public_hooks[hook_type] = LazyBaseFunction(
                    function_dict=v,
                    # function_fields=[],
                )
            elif re.match(r'^[a-zA-Z0-9\_]*(<\_)$', k):
                hook_type = k[:-2]
                # context.private_context[hook_type] = LazyBaseFunction(
                #     function_dict=v,
                #     # function_fields=[],
                # )
                context.private_hooks[hook_type] = LazyBaseFunction(
                    function_dict=v,
                    # function_fields=[],
                )
        return

    if os.path.basename(file_path).split('.')[-1] != "py":
        # Only import python files
        return

    # TODO: RM after dealing with namespace issue for validators
    # Use a unique RUN_ID to prevent duplicate validator errors
    # https://github.com/robcxyz/tackle/issues/43
    # _run_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    # module_name = mod_name + '.hooks.' + file_base[0] + _run_id
    # TODO: Correct version
    # module_name = mod_name + '.hooks.' + file_base[0]
    # TODO: Hack
    try:
        module_name = mod_name + '.hooks.' + file_base[0] + context.run_id
    except AttributeError:
        pass

    loader = importlib.machinery.SourceFileLoader(module_name, file_path)

    if sys.version_info.minor < 10:
        mod = loader.load_module()
    else:
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        loader.exec_module(mod)

    for k, v in mod.__dict__.items():
        if (
            isinstance(v, ModelMetaclass)
            and 'hook_type' in v.__fields__
            and k != 'BaseHook'
            and v.__fields__['hook_type'].default is not None
        ):
            # self[v.__fields__['/hook_type'].default] = v
            context.private_hooks[v.__fields__['hook_type'].default] = v


def import_hooks_from_dir(
    context: 'Context',
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
                import_hook_from_path(context, mod_name, f)
            except (ModuleNotFoundError, ConfigError, ImportError):
                logger.debug(f"Skipping importing {f}")
                continue
        else:
            import_hook_from_path(context, mod_name, f)


def import_with_fallback_install(
    context: 'Context',
    mod_name: str,
    path: str,
    skip_on_error: bool = False,
):
    """
    Import a module and on import error, fallback on requirements file and try to
     import again.
    """
    try:
        import_hooks_from_dir(context, mod_name, path, skip_on_error)
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
        import_hooks_from_dir(context, mod_name, path)
