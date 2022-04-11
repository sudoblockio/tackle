from typing import Union

from tackle.models import Context
from tackle.parser import update_source
from tackle.utils.paths import find_nearest_tackle_file
from tackle.exceptions import NoInputOrParentTackleException


def get_global_kwargs(kwargs):
    """Check for unknown kwargs and return so they can be consumed later."""
    global_kwargs = {}
    for k, v in kwargs.items():
        if k not in Context.__fields__:
            global_kwargs.update({k: v})
    if global_kwargs == {}:
        return None
    return global_kwargs


def tackle(
    *args,
    **kwargs,
) -> Union[dict, list]:
    """
    Run Tackle Box just as if using it from the command line.

    :param checkout: The branch, tag or commit ID to checkout after clone.
    :param no_input: Prompt the user at command line for manual configuration?
    :param context_file: The file to load to set the context, ie list of prompts.
        Defaults to tackle.yaml then cookiecutter.json.
    :param existing_context: A string pointing to a json/yaml or dictionary to use as
        additional context when rendering items.
    :param password: The password to use when extracting the repository.
    :param directory: Relative path to a cookiecutter template in a repository.

    :return: Dictionary of the output
    """
    if args:
        kwargs['input_string'] = args[0]
        if len(args) != 1:
            kwargs['global_args'] = []
            for i in range(1, len(args)):
                kwargs['global_args'].append(args[i])

    # Handle empty calls which fallback to finding the closest tackle file
    # in the parent directory
    if 'input_string' not in kwargs or kwargs['input_string'] is None:
        kwargs['input_string'] = find_nearest_tackle_file()

    # Handle the exception if no tackle file is found in parent directory
    if kwargs['input_string'] is None:
        raise NoInputOrParentTackleException("No input or tackle file has been given.")

    # Initialize context
    context = Context(**kwargs)
    if 'global_kwargs' not in kwargs:
        # When tackle is called from the cli it already has the kwargs.  This is a hack
        # to get this function to accept dicts the same as they would be for use as a
        # package - ie tackle('input-file.yaml', **some_override_dict)
        context.global_kwargs = get_global_kwargs(kwargs)

    # Main loop
    update_source(context)

    return context.public_context
