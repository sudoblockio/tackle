# -*- coding: utf-8 -*-

"""Generate the context based on overwrites and existing contexts."""
import os
import logging
from collections import OrderedDict

from cookiecutter.utils.reader import read_config_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cookiecutter.models import Context, Source
    from cookiecutter.configs import Settings


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


def generate_context(c: 'Context', s: 'Source', settings: 'Settings'):
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
