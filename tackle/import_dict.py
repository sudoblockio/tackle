import os
import logging
import subprocess
import sys
import importlib.machinery
from pydantic import BaseModel, ConfigError
from pydantic.main import ModelMetaclass

# from tackle.models import BaseHook, LazyImportHook
from tackle.utils.paths import listdir_absolute

logger = logging.getLogger(__name__)


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
        if issubclass(v, BaseHook) and not isinstance(v, BaseHook):
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
            )

            # hook = BaseHook(
            #     None,
            #     skip_import=True,
            #     hook_type=h,
            #     hooks_path=hooks_path,
            # )
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


if __name__ == '__main__':
    import time

    start_time = time.time()
    # native_provider_paths = get_native_provider_paths()
    pd = {}
    import_native_providers(pd)

    print("--- %s seconds ---" % (time.time() - start_time))
