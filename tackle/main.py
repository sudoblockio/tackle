"""
Main entry point for the `tacklebox` command.

The code in this module is also a good example of how to use Tackle as a
library rather than a script.
"""
import logging
import json
from _collections import OrderedDict

from tackle.generate import generate_files
from tackle.utils.paths import rmtree
from tackle.models import Context

# from tackle.repository import update_source

from tackle.parser.context import update_context

# from tackle.settings import get_settings
from tackle.parser.providers import update_providers


logger = logging.getLogger(__name__)


def tackle(
    # template='.',
    # no_input=False,
    # checkout=None,
    # context_file=None,
    # context_key=None,
    # password=None,
    # directory=None,
    # existing_context=None,
    # overwrite_inputs=None,
    # override_inputs=None,
    # replay=None,
    # record=None,
    # rerun=None,
    # output_dir='.',
    # overwrite_if_exists=False,
    # skip_if_file_exists=False,
    # accept_hooks=True,
    # config_file=None,
    # default_config=False,
    # config=None,
    # providers=None,
    *args,
    **kwargs,
):
    """
    Run Tackle Box just as if using it from the command line.

    :param template: A directory containing a project template directory,
        or a URL to a git repository.
    :param checkout: The branch, tag or commit ID to checkout after clone.
    :param no_input: Prompt the user at command line for manual configuration?
    :param context_file: The file to load to set the context, ie list of prompts.
        Defaults to tackle.yaml then cookiecutter.json.
    :param context_key: The key to all the context under - defaults to the name
        of the context file minus the file extension.
    :param existing_context: An additional dictionary to use in rendering
        additional prompts.
    :param override_inputs: A dictionary or string pointing to a file to override
        any prompt based inputs.
    :param overwrite_inputs: A dictionary or string pointing to a file to overwrite
        a key and prevent a hook from being called.
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
    if args:
        # setattr(kwargs, 'template', args)
        kwargs['template'] = args[0]
    context = Context(
        # settings=get_settings(
        #     config_file=config_file,
        #     config=config,
        #     default_config=default_config,
        # ),
        # config_file=config_file,
        # config=config,
        # default_config=default_config,
        # no_input=no_input,
        # replay=replay,
        # record=record,
        # rerun=rerun,
        # template=template,
        # checkout=checkout,
        # context_file=context_file,
        # password=password,
        # directory=directory,
        # overwrite_inputs=overwrite_inputs,
        # override_inputs=override_inputs,
        # existing_context=existing_context,
        # context_key=context_key,
        # providers=providers,
        # output_dir=output_dir,
        # overwrite_if_exists=overwrite_if_exists,
        # skip_if_file_exists=skip_if_file_exists,
        # accept_hooks=accept_hooks,
        # template=args,
        **kwargs,
    )
    context.update_source()
    context.update_input_dict()

    # Get the providers
    update_providers(context)
    # Main parsing logic
    update_context(context)

    # output = Output(
    #     output_dir=output_dir,
    #     overwrite_if_exists=overwrite_if_exists,
    #     skip_if_file_exists=skip_if_file_exists,
    #     accept_hooks=accept_hooks,
    # )
    generate_files(context=context)

    # Cleanup (if required)
    if context.cleanup:
        rmtree(context.repo_dir)

    if isinstance(context, OrderedDict):
        context = json.loads(json.dumps(context))

    return context.output_dict
