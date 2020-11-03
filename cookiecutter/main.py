"""
Main entry point for the `cookiecutter` command.

The code in this module is also a good example of how to use Cookiecutter as a
library rather than a script.
"""
import logging
import json
from _collections import OrderedDict

from cookiecutter.generate import generate_files
from cookiecutter.utils.paths import rmtree
from cookiecutter.configs.config_base import get_settings
from cookiecutter.models import Context, Mode, Output, Source
from cookiecutter.repository import update_source
from cookiecutter.parser import update_context

logger = logging.getLogger(__name__)


def cookiecutter(
    template='.',
    no_input=False,
    checkout=None,
    context_file=None,
    context_key=None,
    password=None,
    directory=None,
    existing_context=None,
    override_inputs=None,
    replay=None,
    record=None,
    rerun=None,
    output_dir='.',
    overwrite_if_exists=False,
    skip_if_file_exists=False,
    accept_hooks=True,
    config_file=None,
    env_file=None,
    default_config=False,
    config=None,
    calling_directory=None,
):
    """
    Run Cookiecutter just as if using it from the command line.

    :param template: A directory containing a project template directory,
        or a URL to a git repository.
    :param checkout: The branch, tag or commit ID to checkout after clone.
    :param no_input: Prompt the user at command line for manual configuration?
    :param context_file: The file to load to set the context, ie list of prompts.
        Defaults to nuki.yaml, nukikata.yml, then cookiecutter.json.
    :param context_key: The key to all the context under - defaults to the name
        of the context file minus the file extension.
    :param existing_context: An additional dictionary to use in rendering
        additional prompts.
    :param override_inputs: A dictionary of context that overrides default
        and user configuration.
    :param replay: Do not prompt for input, instead read from saved json. If
        ``True`` read from the ``replay_dir``.
        if it exists
    :param output_dir: Where to output the generated project dir into.
    :param password: The password to use when extracting the repository.
    :param directory: Relative path to a cookiecutter template in a repository.
    :param accept_hooks: Accept pre and post hooks if set to `True`.
    :param config_file: User configuration file path.
    :param default_config: Use default values rather than a config file.

    :return Dictionary of output
    """
    settings = get_settings(
        config_file=config_file,
        env_file=env_file,
        config=config,
        default_config=default_config,
    )

    mode = Mode(no_input=no_input, replay=replay, record=record, rerun=rerun)

    source = Source(
        template=template,
        checkout=checkout,
        no_input=no_input,
        context_file=context_file,
        password=password,
        directory=directory,
    )
    update_source(source=source, settings=settings, mode=mode)

    context = Context(
        context_file=context_file,
        default_context=settings.default_context,
        override_inputs=override_inputs,
        existing_context=existing_context,
        context_key=context_key,
        tackle_gen=source.tackle_gen,
        calling_directory=calling_directory,
    )
    update_context(c=context, s=source, m=mode, settings=settings)

    output = Output(
        output_dir=output_dir,
        overwrite_if_exists=overwrite_if_exists,
        skip_if_file_exists=skip_if_file_exists,
        accept_hooks=accept_hooks,
    )
    generate_files(o=output, c=context, s=source, m=mode, settings=settings)

    # Cleanup (if required)
    if source.cleanup:
        rmtree(source.repo_dir)

    if isinstance(context, OrderedDict):
        context = json.loads(json.dumps(context))

    return context.output_dict
