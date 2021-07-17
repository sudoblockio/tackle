# -*- coding: utf-8 -*-

"""Parser for importing providers into the runtime."""
import os
import logging
import subprocess
import sys
import importlib.machinery

from tackle.providers import native_providers
from tackle.utils.paths import listdir_absolute
from tackle.models import Provider

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context

logger = logging.getLogger(__name__)


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


def get_provider_from_dir(mod_name, path):
    """Initialize the provider from a path."""
    import_with_fallback_install(mod_name, path)
    p = Provider(path=path, name=mod_name)
    return p


def import_hooks_from_dir(
    mod_name, path, excluded_file_names=None, excluded_file_extensions=None
):
    """Import hooks from a directory.

    This is meant to be used by generically pointing to a hooks directory and
    importing all the relevent hooks into the context.
    """
    if excluded_file_names is None:
        excluded_file_names = ['pre_gen_project', 'post_gen_project', '__pycache__']
    if excluded_file_extensions is None:
        excluded_file_extensions = ['pyc']

    # if mod_name == 'tackle.providers.art':
    #     print('debug')

    for f in listdir_absolute(path):
        if os.path.basename(f).split('.')[0] in excluded_file_names:
            continue
        if os.path.basename(f).split('.')[-1] in excluded_file_extensions:
            continue
        import_module_from_path(mod_name + '.' + os.path.basename(f).split('.')[0], f)


def import_module_from_path(mod, path):
    """Import a module from a path presumably with hooks in it."""
    # logger.debug(f"Importing module from path={path} as mod={mod}")
    loader = importlib.machinery.SourceFileLoader(mod, path)
    mod = loader.load_module()
    return mod


def append_provider_dicts(input_providers, context: 'Context'):
    """Update the provider list with a new provider."""
    if isinstance(input_providers, str):
        # For providers from the context
        input_providers = [input_providers]
    elif isinstance(input_providers, dict):
        raise NotImplementedError(
            f"Input provider '{input_providers}' needs to be list."
        )
    logger.debug(f"Importing {input_providers}")
    for i in input_providers:
        # if isinstance(context.provider_dict, str):
        #     context.provider_dict = ""

        mod_name = 'tackle.providers.' + os.path.basename(i)
        hooks_init_path = os.path.join(i, 'hooks', '__init__.py')
        hooks_path = os.path.join(i, 'hooks')
        # logger.debug(f"Importing hook from provider={i} from path={hooks_path}")
        if os.path.isfile(hooks_init_path):
            mod = import_module_from_path(mod_name, hooks_init_path)
            try:
                hook_types = mod.hook_types
                p = Provider(path=hooks_path, hook_types=hook_types, name=mod_name)
                logger.debug(
                    f"Importing hook_types {mod.hook_types} from {hooks_path}."
                )
                context.providers.append(p)
                continue
            except AttributeError:
                logger.debug(f"No hook_types in {hooks_path}, importing module.")
        # elif os.listdir(os.path.join(i, 'hooks')):

        # elif os.path.isdir(hooks_path):
        #     for i in [j for j in os.listdir(hooks_path) if j not in ['__pycache__']]:
        #         import_module_from_path(mod_name, os.path.join(hooks_path, i))

        # This pass will import all the modules and when retrieving hook types,
        # wil search based on all subclasses
        context.providers.append(get_provider_from_dir(mod_name, hooks_path))
        continue


def update_providers(context: 'Context'):
    """
    Update the source with providers and hooks.

    1. Check if the settings provider has been updated
    2. Check if the local provider has been updated
    3. Check if the context has additional providers

    :return: List of Provider objects
    """
    if not context.providers:
        context.providers = []
        # Native providers are gathered from
        append_provider_dicts(native_providers, context)

    # Get provider dirs
    if context.settings.extra_providers:
        # Providers from config file
        append_provider_dicts(context.settings.extra_providers, context)

    # If any special providers are provided in the context file with the `__providers` key
    if '__providers' in context.input_dict[context.context_key]:
        append_provider_dicts(
            context.input_dict[context.context_key]['__providers'], context
        )

    # TODO: Automatically import hooks
    # hooks_dir = os.path.join(context.repo_dir, 'hooks')
    # if os.path.isdir(os.path.join(context.repo_dir, 'hooks')):
    #     append_provider_dicts()
