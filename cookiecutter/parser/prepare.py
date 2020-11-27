# -*- coding: utf-8 -*-

"""Generate the context based on overwrites and existing contexts."""
import os
import logging
import importlib.util
from collections import OrderedDict

from cookiecutter.utils.paths import expand_paths
from cookiecutter.utils.reader import read_config_file
from cookiecutter.repository import update_source

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cookiecutter.models import Context, Source, Providers, Provider, Mode, Settings
    # from cookiecutter.configs import Settings


logger = logging.getLogger(__name__)


def apply_overwrites_to_inputs(input, overwrite_dict):
    """Modify the given context in place based on the overwrite_context."""
    for variable, overwrite in overwrite_dict.items():
        if variable not in input:
            # Do not include variables which are not used in the template
            continue

        context_value = input[variable]

        if isinstance(context_value, list):
            # We are dealing with a choice variable
            if overwrite in context_value:
                # This overwrite is actually valid for the given context
                # Let's set it as default (by definition first item in list)
                # see ``cookiecutter.prompt.prompt_choice_for_config``
                context_value.remove(overwrite)
                context_value.insert(0, overwrite)
        else:
            # Simply overwrite the value for this variable
            input[variable] = overwrite


def prepare_context(c: 'Context', s: 'Source', settings: 'Settings'):
    """Generate the context for a Cookiecutter project template.

    Loads the JSON file as a Python object, with key being the JSON filename.

    :param context_file: JSON file containing key/value pairs for populating
        the cookiecutter's variables.
    :param default_context: Dictionary containing config to take into account.
    :param extra_context: Dictionary containing configuration overrides
    """
    c.input_dict = OrderedDict([])

    obj = read_config_file(s.context_file)

    # Add the Python object to the context dictionary
    if not c.context_key:
        file_name = os.path.split(c.context_file)[1]
        file_stem = file_name.split('.')[0]
        c.input_dict[file_stem] = obj
    else:
        c.input_dict[c.context_key] = obj

    # Overwrite context variable defaults with the default context from the
    # user's global config, if available
    if settings.default_context:
        apply_overwrites_to_inputs(obj, settings.default_context)

    if c.overwrite_inputs:
        apply_overwrites_to_inputs(obj, c.overwrite_inputs)
    else:
        c.overwrite_inputs = OrderedDict()

    if not c.override_inputs:
        c.override_inputs = OrderedDict()

    # include template dir or url in the context dict
    c.input_dict[c.context_key]['_template'] = s.repo_dir

    logger.debug('Context generated is %s', c.input_dict)


def get_providers(p: 'Providers', c: 'Context', s: 'Source', settings: 'Settings'):
    """Update the source with providers and hooks.

    1. Check if the settings provider has been updated
    2. Check if the local provider has been updated
    3. Check if the context has additional providers

    :param c:
    :param s:
    :param settings:
    :return:
    """
    # if len(p) > 0:
    # for i in [os.path.abspath(n) for n in os.listdir(os.path.join(
    # os.path.dirname(__file__), 'providers')) if os.path.isdir(os.path.join(
    # os.path.dirname(__file__), 'providers', n))]:
    #     self.provider_paths.append(i)
    # Get provider dirs
    if settings.extra_providers:
        # Providers from config file
        append_provider_dicts(p, settings.extra_providers)

    if '__providers' in c.input_dict:
        append_provider_dicts(p, c.input_dict['__providers'])

    # Get provider hook types
    # for i in p.provider_paths:
    #     mod = import_module(i)


def interpret_provider_str(
    context_provider: str, settings: 'Settings', m: 'Mode'
) -> str:
    """"""
    # Pass to sources import logic and pull in source to provider
    provider_source = Source(template=context_provider)
    provider_source = update_source(provider_source, settings, m)
    # TODO: This won't work unless we modify the sourcing function to accept both provider
    # based dirs or template dirs
    pass
    return 'provider_dir'


def get_provider_dirs():
    pass


def get_provider_hook_types():
    pass


def append_provider_dicts(p: 'Providers', input_providers):
    """Update the provider list with a new provider."""
    if isinstance(input_providers, str):
        input_providers = [input_providers]
    elif isinstance(input_providers, dict):
        raise ValueError(f"Input provider '{input_providers}' needs to be list.")

    for i in input_providers:
        provider = initialize_provider(i)
        p.provider_paths.append(provider)

        # if provider.name in [i.name for i in p.providers]:
        #     # Replace the provider with the one in settings if the name conflicts
        #     # ie - this overrides the native provider or any preceding import
        #     initialize_provider()
        #     # p.providers = [i for i in p.providers if i.get('hook_types') != provider.hook_types]
        #     p.providers.append()
        # else:


def initialize_provider(raw) -> 'Provider':
    """Take the raw input and send through parsing logic to initialize the provider."""
    if isinstance(raw, str):
        # Send into source logic
        raise NotImplementedError
    elif isinstance(raw, list):
        for i in raw:
            pass
        # Send into source logic
        raise NotImplementedError

    provider = Provider(**raw)
    if not provider.path:
        get_path_from_src(provider)
    else:
        fix_provider_path(provider)

    return Provider(**provider)


def fix_provider_path(provider):
    raise NotImplementedError


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


def clone_provider():
    pass


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
    if not os.path.exists(
        os.path.join(
            settings.tackle_dir, 'providers', git_parts[0], git_parts[1], git_parts[2]
        )
    ):
        clone_provider()

    pass


def get_hooks(setting: 'Settings') -> list:
    """Gets providers from various locations.

    1. Native hooks from local `providers` directory
    2. Imports from directories from settings
    3. Imports as defined from an operator
    """
    hooks = []
    hooks = hooks + get_hooks_from_providers(get_native_providers())

    if setting.extra_provider_dirs:
        try:
            hooks = hooks + get_hooks_from_providers(
                [expand_paths(i) for i in setting.extra_provider_dirs]
            )
        except:
            logger.warning("")

    # hooks = hooks + get_hooks_from_providers()
    return hooks


def get_hooks_from_providers(provider_paths: list) -> list:
    hooks = []
    for i in provider_paths:
        p = import_module(i)
        try:
            hooks = hooks + p.hooks
        except AttributeError:
            logger.debug(f"No hooks found in {i} provider.")
    return hooks


def get_native_providers() -> list:
    """Get list of native providers."""
    providers = []
    for i in [
        n
        for n in os.listdir(os.path.dirname(os.path.abspath(__file__)))
        if os.path.isdir(n)
    ]:
        providers.append(i)
    return providers


def import_module(mod):
    spec = importlib.util.find_spec(mod)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
