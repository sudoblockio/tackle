# -*- coding: utf-8 -*-

"""Parser for importing providers into the runtime."""
import re
import os
import logging
import subprocess
import sys
import importlib.machinery
import inspect
from tackle.providers import native_providers
from tackle.utils.paths import listdir_absolute
from tackle.repository import is_git_repo
from tackle.exceptions import UnknownHookTypeException
from tackle.models import Provider, BaseHook

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context, Source, Mode, Settings

logger = logging.getLogger(__name__)


# TODO: Integrate with parsing the input provider strings for DL from GH
def parse_git_src_str(git_repo: str):
    """Decompose a repo - UNUSED ATM."""
    if re.compile(r"(git@[\w\.]+)").match(git_repo):
        # Check if ssh based
        git_repo = re.sub('.git', '', git_repo)
        git_suffix = git_repo.split(':')[-1]
        git_parts = git_suffix.split('/')
        return git_parts

    if re.compile(r"(https:\/\/[\w\.]+)").match(git_repo):
        # Check if https based
        git_suffix = git_repo.split('//')[-1]
        git_parts = git_suffix.split('/')[1:]
        return git_parts


def get_path_from_src(provider: 'Provider', settings: 'Settings', mode: 'Mode'):
    """Get a path from source - UNUSED ATM."""
    if is_git_repo(provider.src):
        git_parts = parse_git_src_str(provider.src)
    else:
        raise NotImplementedError("Needs to be a git repo right now.")

    if provider.version:
        git_parts.append(provider.version)
    else:
        git_parts.append("master")


def install_requirements_if_exists(path, requirements_file='requirements.txt'):
    """Install the requirements.txt file if it exists in path."""
    requirements_file = os.path.join(path, requirements_file)
    if os.path.isfile(requirements_file):
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--disable-pip-version-check",
                "-r",
                requirements_file,
            ]
        )


def import_with_fallback_install(mod_name, path):
    """Import a module and on import error, fallback on requirements file."""
    try:
        import_hooks_from_dir(mod_name, path)
    except ModuleNotFoundError:
        install_requirements_if_exists(os.path.dirname(path))
        import_hooks_from_dir(mod_name, path)


def get_provider_from_dir(mod_name, path):
    """Initialize the provider from a path."""
    import_with_fallback_install(mod_name, path)
    p = Provider(path=path, name=mod_name)
    return p


def import_hooks_from_dir(
        mod_name,
        path,
        excluded_file_names=None,
        excluded_file_extensions=None
):
    """Import hooks from a directory.

    This is meant to be used by generically pointing to a hooks directory and
    importing all the relevent hooks into the context.
    """
    if excluded_file_names is None:
        excluded_file_names = ['pre_gen_project', 'post_gen_project', '__pycache__']
    if excluded_file_extensions is None:
        excluded_file_extensions = ['pyc']

    for f in listdir_absolute(path):
        if os.path.basename(f).split('.')[0] in excluded_file_names:
            continue
        if os.path.basename(f).split('.')[-1] in excluded_file_extensions:
            continue
        import_module_from_path(mod_name + '.' + os.path.basename(f).split('.')[0], f)


def get_hook(hook_type, context: 'Context'):
    """
    Get the hook from available providers.

    Does the following to return the hook:
    1. Check if hook hasn't been imported already
    2. Check if the hook has been declared in a provider's __init__.py's
    `hook_types` field.
    3. Try to import it then fall back on installing the requirements.txt file
    """
    for h in BaseHook.__subclasses__():
        if hook_type == inspect.signature(h).parameters['type'].default:
            return h

    for p in context.providers:
        if hook_type in p.hook_types:
            import_with_fallback_install(p.name, p.path)

    for h in BaseHook.__subclasses__():
        if hook_type == inspect.signature(h).parameters['type'].default:
            return h

    avail_hook_types = [
        inspect.signature(i).parameters['type'].default
        for i in BaseHook.__subclasses__()
    ]
    logger.debug(f"Available hook types = {avail_hook_types}")
    raise UnknownHookTypeException(
        f"The hook type=\"{hook_type}\" is not available in the providers. "
        f"Run the application with `--verbose` to see available hook types."
    )


def import_module_from_path(mod, path):
    """Import a module from a path presumably with hooks in it."""
    logger.debug(f"Importing module from path={path} as mod={mod}")
    loader = importlib.machinery.SourceFileLoader(mod, path)
    mod = loader.load_module()
    return mod


def append_provider_dicts(input_providers, context: 'Context', mode: 'Mode'):
    """Update the provider list with a new provider."""
    if isinstance(input_providers, str):
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
        logger.debug(f"Importing hook from provider={i} from path={hooks_path}")
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


def get_providers(
        context: 'Context', source: 'Source', settings: 'Settings', mode: 'Mode'
) -> ['Provider']:
    """
    Update the source with providers and hooks.

    1. Check if the settings provider has been updated
    2. Check if the local provider has been updated
    3. Check if the context has additional providers

    :return: List of Provider objects
    """
    if len(context.providers) == 0:
        # Native providers are gathered from
        append_provider_dicts(native_providers, context, mode)

    # Get provider dirs
    if settings.extra_providers:
        # Providers from config file
        append_provider_dicts(settings.extra_providers, context, mode)

    if '__providers' in context.input_dict[context.context_key]:
        append_provider_dicts(
            context.input_dict[context.context_key]['__providers'], context, mode
        )

    # hooks_dir = os.path.join(source.repo_dir, 'hooks')
    # if os.path.isdir(os.path.join(source.repo_dir, 'hooks')):
    #     append_provider_dicts()
