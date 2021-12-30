"""Parser for importing providers into the runtime."""
import os
import logging
from pathlib import Path
import subprocess
import sys
import importlib.machinery
from pydantic import BaseModel

from tackle.utils.paths import listdir_absolute, work_in
from tackle.settings import settings

from typing import List

logger = logging.getLogger(__name__)

file_path = os.path.dirname(os.path.abspath(__file__))

native_providers = [
    os.path.join(file_path, f)
    for f in os.listdir(file_path)
    if os.path.isdir(os.path.join(file_path, f)) and f != '__pycache__'
]


class Provider(BaseModel):
    """Base provider."""

    path: str = None
    hooks_path: str = None
    hook_types: list = []
    hook_modules: list = []

    name: str = None  # defaults to os.path.basename(path)

    src: str = None
    version: str = None
    requirements: list = []

    def __init__(self, **data):
        super().__init__(**data)


class ProviderList(BaseModel):
    """
    Provider list object that on instantiation imports native (shipping wit tackle box),
    settings (declared in ~/.tackle/settings.yaml), and local (in a local hooks
    directory).
    """

    __root__: List[Provider] = []
    # _functions: dict = None

    @property
    def hook_types(self):
        hook_types = []
        for i in self:
            hook_types.append(i.name)
        return hook_types

    # @property
    # def functions(self):
    #     functions = {}
    #     for i in self:
    #         functions.append(i.functions)
    #     return functions

    def append(self, value: Provider):
        """Override."""
        self.__root__.append(value)

    def __iter__(self):
        """Override."""
        return iter(self.__root__)

    def __getitem__(self, item):
        """Override."""
        return self.__root__[item]

    def __init__(self, **data):
        super().__init__(**data)
        """Import natve, settings, and local providers."""
        # Import native providers in tackle.providers
        self.import_paths(native_providers)
        # Import any providers in settings
        if settings.extra_providers:
            self.import_paths(settings.extra_providers)
        # If there is a hooks directory in the same dir as execution, import those
        if 'hooks' in os.listdir():
            curent_dir_provider_name = Path().parent.absolute().name
            with work_in(".."):
                self.import_paths([curent_dir_provider_name])

    def import_paths(self, provider_paths):
        """Iterate through paths and import them."""
        for i in provider_paths:
            self.append_from_path(i)

    def append_from_path(self, provider_path):
        """Append a provider with a given path."""
        mod_name = 'tackle.providers.' + os.path.basename(provider_path)
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

            try:
                hook_types = mod.hook_types
                p = Provider(path=hooks_path, hook_types=hook_types, name=mod_name)
                logger.debug(
                    f"Importing hook_types {mod.hook_types} from {hooks_path}."
                )
                self.append(p)
            except AttributeError:
                logger.debug(
                    f"No `hook_types` declared in {hooks_path}, importing module."
                )
                import_with_fallback_install(mod_name, hooks_path)
        else:
            # This pass will import all the modules and when retrieving hook types,
            # wil search based on all subclasses
            # self.append(get_provider_from_dir(mod_name, hooks_path))
            import_with_fallback_install(mod_name, hooks_path)

            p = Provider(path=hooks_path, name=mod_name)
            self.append(p)


def import_with_fallback_install(mod_name, path):
    """Import a module and on import error, fallback on requirements file."""
    try:
        import_hooks_from_dir(mod_name, path)
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
        import_hooks_from_dir(mod_name, path)


# def get_provider_from_dir(mod_name, path):
#     """Initialize the provider from a path."""
#     import_with_fallback_install(mod_name, path)
#     p = Provider(path=path, name=mod_name)
#     return p


def import_hooks_from_dir(
    mod_name,
    path,
    excluded_file_names=None,
    excluded_file_extensions=None,
):
    """
    Import hooks from a directory.

    This is meant to be used by generically pointing to a hooks directory and
    importing all the relevant hooks into the context.
    """
    if excluded_file_names is None:
        # Maintaining cookiecutter support here?
        excluded_file_names = ['pre_gen_project', 'post_gen_project', '__pycache__']
    if excluded_file_extensions is None:
        excluded_file_extensions = ['pyc']

    potential_hooks = listdir_absolute(path)
    for f in potential_hooks:
        file_base = os.path.basename(f).split('.')
        if file_base[0] in excluded_file_names:
            continue
        if file_base[-1] in excluded_file_extensions:
            continue

        if os.path.basename(f).split('.')[-1] != "py":
            # Only import python files
            continue

        loader = importlib.machinery.SourceFileLoader(
            mod_name + '.' + os.path.basename(f).split('.')[0], f
        )
        loader.load_module()
