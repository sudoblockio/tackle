"""
Main entry point for the `tacklebox` command.

The code in this module is also a good example of how to use Tackle as a
library rather than a script.
"""
import logging

from tackle.generate import generate_files
from tackle.utils.paths import rmtree
from tackle.models import Context
from tackle.parser import walk_context, update_source

# from tackle.context import update_context
# from tackle.providers import update_providers

# from tackle.input_dict import update_input_dict
# from tackle.source import update_source

logger = logging.getLogger(__name__)


def tackle(
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
        kwargs['input_string'] = args[0]

    context = Context(**kwargs)

    update_source(context)

    # TODO: Update with hook
    generate_files(context=context)

    # Cleanup (if required)
    if context.cleanup:
        rmtree(context.repo_dir)

    from tackle.utils.dicts import remove_private_vars

    # remove_private_vars(context=context)

    # if isinstance(context, OrderedDict):
    #     context = json.loads(json.dumps(context))

    return context.output_dict
