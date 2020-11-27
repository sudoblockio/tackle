import os
import logging
import importlib.util
from cookiecutter.providers import native_providers

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cookiecutter.models import Context, Source, Providers, Provider, Mode, Settings


def get_providers(
    p: 'Providers', c: 'Context', s: 'Source', settings: 'Settings', mode: 'Mode'
) -> Providers():
    """Update the source with providers and hooks.

    1. Check if the settings provider has been updated
    2. Check if the local provider has been updated
    3. Check if the context has additional providers

    :param c:
    :param s:
    :param settings:
    :return:
    """
    if len(p.providers) > 0:
        append_provider_dicts(native_providers, p, settings, mode)

    # Get provider dirs
    if settings.extra_providers:
        # Providers from config file
        append_provider_dicts(settings.extra_providers, p)

    if '__providers' in c.input_dict:
        append_provider_dicts(c.input_dict['__providers'], p)


def append_provider_dicts(
    input_providers, p: 'Providers', settings: 'Settings', mode: 'Mode'
):
    """Update the provider list with a new provider."""
    if isinstance(input_providers, str):
        input_providers = [input_providers]
    elif isinstance(input_providers, dict):
        raise ValueError(f"Input provider '{input_providers}' needs to be list.")

    for i in input_providers:
        provider = initialize_provider(i, settings, mode)
        p.providers.append(provider)

        # if provider.name in [i.name for i in p.providers]:
        #     # Replace the provider with the one in settings if the name conflicts
        #     # ie - this overrides the native provider or any preceding import
        #     initialize_provider()
        #     # p.providers = [i for i in p.providers if i.get('hook_types') != provider.hook_types]
        #     p.providers.append()
        # else:


def initialize_provider(raw, settings: 'Settings', mode: 'Mode') -> 'Provider':
    """Take the raw input and send through parsing logic to initialize the provider."""
    if isinstance(raw, str):
        if os.path.isdir(raw):
            if os.path.isfile(os.path.join(raw, '__init__.py')):
                mod = import_module_from_path(os.path.basename(raw), raw)
                return Provider(path=raw, hook_types=mod.hook_types)
            else:
                raise NotImplementedError

        if os.path.isfile(raw):
            raise NotImplementedError
        else:
            raise NotImplementedError
    elif isinstance(raw, list):
        for i in raw:
            pass
        # Send into source logic
        raise NotImplementedError

    # provider = Provider(**raw)
    # if not provider.path:
    #     get_path_from_src(provider)
    # else:
    #     fix_provider_path(provider)
    # return Provider(**provider)


def get_provider_dirs():
    pass


def get_provider_hook_types():
    pass


def import_module_from_path(mod, path):
    """"""

    spec = importlib.util.spec_from_file_location(mod, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_provider_layout(path):
    pass


def fix_provider_path(provider):
    # This should
    pass


def parse_git_src_str(git_repo: str):
    import re

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
    from cookiecutter.repository import is_git_repo

    if is_git_repo(provider.src):
        git_parts = parse_git_src_str(provider.src)
    else:
        raise NotImplementedError("Needs to be a git repo right now.")

    if provider.version:
        git_parts.append(provider.version)
    else:
        git_parts.append("master")

    # Check if package exists in local
    # if not os.path.exists(os.path.join(settings.tackle_dir, 'providers', git_parts[0], git_parts[1], git_parts[2])):
    #     clone_provider()
    # pass
