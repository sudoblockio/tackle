# -*- coding: utf-8 -*-

"""Parser for importing providers into the runtime."""
import os
import logging
import subprocess
import sys
import importlib.machinery

from tackle.utils.paths import listdir_absolute, is_repo_url, work_in
from tackle.utils.vcs import clone
from tackle.settings import settings

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from tackle.models import Context

logger = logging.getLogger(__name__)

from pydantic import BaseModel

file_path = os.path.dirname(os.path.abspath(__file__))

native_providers = [
    os.path.join(file_path, f)
    for f in os.listdir(file_path)
    if os.path.isdir(os.path.join(file_path, f)) and f != '__pycache__'
]


print()


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
    __root__: List[Provider] = []

    @property
    def hook_types(self):
        hook_types = []
        for i in self:
            hook_types.append(i.name)
        return hook_types

    def append(self, value: Provider):
        self.__root__.append(value)

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __init__(self, **data):
        super().__init__(**data)
        # append_provider_dicts(native_providers, context)
        # append_provider_dicts(settings.extra_providers, context)
        self.import_paths(native_providers)
        if settings.extra_providers:
            self.import_paths(settings.extra_providers)

    def import_paths(self, provider_paths):
        for i in provider_paths:
            self.append_from_path(i)

    def append_from_path(self, provider_path):
        """Appends a provider with a given path."""
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
    mod_name, path, excluded_file_names=None, excluded_file_extensions=None
):
    """
    Import hooks from a directory.

    This is meant to be used by generically pointing to a hooks directory and
    importing all the relevant hooks into the context.
    """
    if excluded_file_names is None:
        excluded_file_names = ['pre_gen_project', 'post_gen_project', '__pycache__']
    if excluded_file_extensions is None:
        excluded_file_extensions = ['pyc']

    potential_hooks = listdir_absolute(path)
    for f in potential_hooks:
        if os.path.basename(f).split('.')[0] in excluded_file_names:
            continue
        if os.path.basename(f).split('.')[-1] in excluded_file_extensions:
            continue
        if os.path.basename(f).split('.')[-1] != "py":
            # Only import python files
            continue

        loader = importlib.machinery.SourceFileLoader(
            mod_name + '.' + os.path.basename(f).split('.')[0], f
        )
        mod = loader.load_module()
        # import_module_from_path(mod_name + '.' + os.path.basename(f).split('.')[0], f)


# def import_module_from_path(mod, path):
#     """Import a module from a path presumably with hooks in it."""
#     loader = importlib.machinery.SourceFileLoader(mod, path)
#     mod = loader.load_module()
#     return mod


# def get_remote_provider(input_provider: str, context: 'Context'):
#     git_org = input_provider.split('/')[-2]
#     provider_name = input_provider.split('/')[-1]
#     provider_org_path = os.path.join(settings.tackle_dir, git_org)
#     provider_path = os.path.join(provider_org_path, provider_name)
#
#     if not os.path.exists(provider_org_path):
#         os.mkdir(provider_org_path)
#
#     if os.path.exists(provider_path):
#         with work_in(provider_path):
#             # Do a git pull
#             pass
#     else:
#         clone(
#             repo_url=input_provider,
#             checkout=context.checkout,
#             clone_to_dir=provider_org_path,
#             no_input=context.no_input,
#         )
#     mod_name = f'tackle.providers.{git_org}.{provider_name}'
#
#     return mod_name, provider_org_path


# def append_provider_dicts(input_providers, context: 'Context'):
#     # """Update the provider list with a new provider.
#     # """
#     """
#     Update .
#
#     :param input_providers: List of
#     """
#     if isinstance(input_providers, str):
#         # For providers from the context
#         input_providers = [input_providers]
#     elif isinstance(input_providers, dict):
#         raise NotImplementedError(
#             f"Input provider '{input_providers}' needs to be string or list."
#         )
#     logger.debug(f"Importing {input_providers}")
#     for i in input_providers:
#         if is_repo_url(i):
#             # Handle remote providers by cloning into ~/.tackle dir
#             mod_name, i = get_remote_provider(i, context)
#         else:
#             mod_name = 'tackle.providers.' + os.path.basename(i)
#
#         hooks_init_path = os.path.join(i, 'hooks', '__init__.py')
#         hooks_path = os.path.join(i, 'hooks')
#
#         # TODO: RM if commands are dead / implicit in BaseHook methods
#         # commands_path = os.path.join(i, 'commands')
#         #
#         # # Handle commands by saving the file name as the command name with the path.
#         # if os.path.isdir(commands_path):
#         #     if context.commands is None:
#         #         context.commands = []
#         #
#         #     for c in os.listdir(commands_path):
#         #         if c.endswith(('yaml', 'yml')):
#         #             context.commands.append(Command(name=c.split('.')[0],
#         #                                             command_path=commands_path,
#         #                                             extension=c.split('.')[1]))
#
#         # If the provider has an __init__.py in the hooks directory, import that
#         # to check if there are any hook types declared there.  If there are, store
#         # those references so that if the hook type is later called, the hook can
#         # then be imported.
#         if os.path.isfile(hooks_init_path):
#             mod = import_module_from_path(mod_name, hooks_init_path)
#             try:
#                 hook_types = mod.hook_types
#                 p = Provider(path=hooks_path, hook_types=hook_types, name=mod_name)
#                 logger.debug(
#                     f"Importing hook_types {mod.hook_types} from {hooks_path}."
#                 )
#                 context.providers.append(p)
#                 # Continue through loop otherwise the module will be imported
#                 continue
#             except AttributeError:
#                 logger.debug(f"No hook_types in {hooks_path}, importing module.")
#
#         # This pass will import all the modules and when retrieving hook types,
#         # wil search based on all subclasses
#         context.providers.append(get_provider_from_dir(mod_name, hooks_path))
#         continue
#
#
# def update_providers(context: 'Context'):
#     """
#     Update the source with providers and hooks.
#
#     1. Check if the settings provider has been updated
#     2. Check if the local provider has been updated
#     3. Check if the context has additional providers
#
#     :return: List of Provider objects
#     """
#     if not context.providers:
#         # Means we are importing providers for the first time
#         context.providers = []
#         # Native providers are gathered from local `tackle/providers` directory
#         append_provider_dicts(native_providers, context)
#
#         # Custom providers are also imported only on first load
#         # Get provider dirs
#         if settings.extra_providers:
#             # Providers from config file
#             append_provider_dicts(settings.extra_providers, context)
#
#     # TODO: Move to within file parsing logic
#     # If any special providers are provided in the context file with the `__providers` key
#     # if '__providers' in context.input_dict[context.context_key]:
#     #     append_provider_dicts(
#     #         context.input_dict[context.context_key]['__providers'], context
#     #     )
#
#     # TODO: Automatically import hooks -> Do not need repo_dir and can
#     #  either search in present directory or recursively search in parent
#     #  directories for a `hooks` directory.
#
#     # hooks_dir = os.path.join(context.repo_dir, 'hooks')
#     # if os.path.isdir(os.path.join(context.repo_dir, 'hooks')):
#     #     append_provider_dicts()


if __name__ == '__main__':
    print(native_providers)
