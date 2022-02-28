# from .console import hooks
# from .paths import hooks

# import os
# import logging
# import subprocess
# import sys
# import importlib.machinery
# from pydantic import BaseModel, ConfigError
#
# from tackle.utils.paths import listdir_absolute
# from tackle.settings import settings
#
# from typing import List
#
# logger = logging.getLogger(__name__)
#
# file_path = os.path.dirname(os.path.abspath(__file__))
#
# native_providers = [
#     os.path.join(file_path, f)
#     for f in os.listdir(file_path)
#     if os.path.isdir(os.path.join(file_path, f)) and f != '__pycache__'
# ]
#
#
# class Provider(BaseModel):
#     """Base provider."""
#
#     path: str = None
#     hooks_path: str = None
#     hook_types: list = []
#     hook_modules: list = []
#
#     name: str = None  # defaults to os.path.basename(path)
#
#     src: str = None
#     version: str = None
#     requirements: list = []
#
#     def __init__(self, **data):
#         super().__init__(**data)
#
#
# class ProviderList(BaseModel):
#     """
#     Provider list object that on instantiation imports native (shipping wit tackle box),
#     settings (declared in ~/.tackle/settings.yaml), and local (in a local hooks
#     directory).
#     """
#
#     __root__: List[Provider] = []
#     # _functions: dict = None
#
#     @property
#     def hook_types(self):
#         hook_types = []
#         for i in self:
#             hook_types.append(i.name)
#         return hook_types
#
#     # @property
#     # def functions(self):
#     #     functions = {}
#     #     for i in self:
#     #         functions.append(i.functions)
#     #     return functions
#
#     def append(self, value: Provider):
#         """Override."""
#         self.__root__.append(value)
#
#     def __iter__(self):
#         """Override."""
#         return iter(self.__root__)
#
#     def __getitem__(self, item):
#         """Override."""
#         return self.__root__[item]
#
#     def __init__(self, **data):
#         super().__init__(**data)
#         """Import natve, settings, and local providers."""
#         # Import native providers in tackle.providers
#         self.import_paths(native_providers)
#         # Import any providers in settings
#         if settings.extra_providers:
#             self.import_paths(settings.extra_providers)
#         # Local `hooks` dir imported within parser
#
#     def import_paths(self, provider_paths):
#         """Iterate through paths and import them."""
#         for i in provider_paths:
#             self.append_from_path(i)
#
#     def append_from_path(self, provider_path):
#         """Append a provider with a given path."""
#         mod_name = 'tackle.providers.' + os.path.basename(provider_path)
#         hooks_init_path = os.path.join(provider_path, 'hooks', '__init__.py')
#         hooks_path = os.path.join(provider_path, 'hooks')
#
#         # If the provider has an __init__.py in the hooks directory, import that
#         # to check if there are any hook types declared there.  If there are, store
#         # those references so that if the hook type is later called, the hook can
#         # then be imported.
#         if os.path.isfile(hooks_init_path):
#             # mod = import_module_from_path(mod_name, hooks_init_path)
#             loader = importlib.machinery.SourceFileLoader(mod_name, hooks_init_path)
#             mod = loader.load_module()
#
#             try:
#                 hook_types = mod.hook_types
#                 p = Provider(path=hooks_path, hook_types=hook_types, name=mod_name)
#                 logger.debug(
#                     f"Importing hook_types {mod.hook_types} from {hooks_path}."
#                 )
#                 self.append(p)
#             except AttributeError:
#                 logger.debug(
#                     f"No `hook_types` declared in {hooks_path}, importing module."
#                 )
#                 # import_with_fallback_install(mod_name, hooks_path)
#         # else:
#         # This pass will import all the modules and when retrieving hook types,
#         # wil search based on all subclasses
#         # self.append(get_provider_from_dir(mod_name, hooks_path))
#         import_with_fallback_install(mod_name, hooks_path, skip_on_error=True)
#
#         p = Provider(path=hooks_path, name=mod_name)
#         self.append(p)
#
#
# def import_with_fallback_install(mod_name, path, skip_on_error: bool = False):
#     """Import a module and on import error, fallback on requirements file."""
#     try:
#         import_hooks_from_dir(mod_name, path, skip_on_error)
#     except ModuleNotFoundError:
#         requirements_path = os.path.join(path, '..', 'requirements.txt')
#         if os.path.isfile(requirements_path):
#             # It is a convention of providers to have a requirements file at the base.
#             # Install the contents if there was an import error
#             subprocess.check_call(
#                 [
#                     sys.executable,
#                     "-m",
#                     "pip",
#                     "install",
#                     "--quiet",
#                     "--disable-pip-version-check",
#                     "-r",
#                     requirements_path,
#                 ]
#             )
#         import_hooks_from_dir(mod_name, path)
#
#
# def import_hooks_from_dir(
#     mod_name,
#     path,
#     skip_on_error: bool = False,
# ):
#     """
#     Import hooks from a directory. This is meant to be used by generically pointing to
#      a hooks directory and importing all the relevant hooks into the context.
#     """
#     potential_hooks = listdir_absolute(path)
#     for f in potential_hooks:
#         if skip_on_error:
#             try:
#                 import_hook_from_path(mod_name, f)
#             except (ModuleNotFoundError, ConfigError):
#                 logger.debug(f"Skipping importing {f}")
#                 continue
#         else:
#             import_hook_from_path(mod_name, f)
#
#
# def import_hook_from_path(
#     mod_name,
#     file_path,
# ):
#     """Import a single hook from a path."""
#     # Maintaining cookiecutter support here as it might have a `hooks` dir.
#     excluded_file_names = ['pre_gen_project', 'post_gen_project', '__pycache__']
#     excluded_file_extensions = ['pyc']
#
#     file_base = os.path.basename(file_path).split('.')
#     if file_base[0] in excluded_file_names:
#         return
#     if file_base[-1] in excluded_file_extensions:
#         return
#
#     if os.path.basename(file_path).split('.')[-1] != "py":
#         # Only import python files
#         return
#
#     loader = importlib.machinery.SourceFileLoader(
#         mod_name + '.' + os.path.basename(file_path).split('.')[0], file_path
#     )
#     loader.load_module()
