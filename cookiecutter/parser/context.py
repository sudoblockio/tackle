# -*- coding: utf-8 -*-

"""Parser for the general context without generic logic."""
import os
import logging
from collections import OrderedDict
from jinja2.exceptions import UndefinedError
from cookiecutter.render import render_variable
from cookiecutter.utils.context_manager import work_in
from cookiecutter.utils.reader import read_config_file, apply_overwrites_to_inputs
from cookiecutter.render.environment import StrictEnvironment
from cookiecutter.exceptions import UndefinedVariableInTemplate
from cookiecutter.parser.prompts import prompt_list, prompt_str, read_user_dict
from cookiecutter.parser.hooks import parse_hook

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cookiecutter.models import Context, Mode, Source, Settings

logger = logging.getLogger(__name__)


def parse_context(c: 'Context', m: 'Mode', s: 'Source'):
    """Parse the context and iterate over values.

    :param dict context: Source for field names and sample values.
    :param env: Jinja environment to render values with.
    :param context_key: The key to insert all the outputs under in the context dict.
    :param no_input: Prompt the user at command line for manual configuration.
    :param existing_context: A dictionary of values to use during rendering.
    :return: cc_dict
    """
    for key, raw in c.input_dict[c.context_key].items():
        c.key = key
        # c.raw = raw
        if m.rerun and c.key in c.override_inputs:
            # If there is a rerun dictionary then insert it in output and proceed.
            c.output_dict[key] = c.override_inputs[key]
            continue
        if key.startswith(u'_') and not key.startswith('__'):
            c.output_dict[key] = raw
            continue
        elif key.startswith('__'):
            c.output_dict[key] = render_variable(c, raw)
            continue

        if key in c.overwrite_inputs:
            c.output_dict[key] = c.overwrite_inputs[key]
            continue

        try:
            if isinstance(raw, list):
                # We are dealing with a choice variable
                c.output_dict[key] = prompt_list(c, m, raw)
            elif isinstance(raw, str):
                # We are dealing with a regular variable
                c.output_dict[key] = prompt_str(c, m, raw)

            elif isinstance(raw, dict):
                # dict parsing logic
                if 'type' not in raw:
                    val = render_variable(c, raw)
                    if not m.no_input:
                        val = read_user_dict(key, val)
                    c.output_dict[key] = val
                else:
                    # Main entrypoint into hook parsing logic
                    parse_hook(c, m, s)

        except UndefinedError as err:
            if m.record or m.rerun:
                # Dump the output context
                pass

            msg = "Unable to render variable '{}'".format(key)
            raise UndefinedVariableInTemplate(msg, err, c.input_dict)

    return c


def prep_context(c: 'Context', m: 'Mode', s: 'Source', settings: 'Settings'):
    """
    Prompt user to enter values.

    Function sets the jinja environment and brings in extensions.

    :param dict c: Source for field names and sample values.
    :param no_input: Prompt the user at command line for manual configuration.
    :param context_key: The key to insert all the outputs under in the context dict.
    :param existing_context: A dictionary of values to use during rendering.
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

    if not c.existing_context:
        c.output_dict = OrderedDict([])
    else:
        c.output_dict = OrderedDict(c.existing_context)

    c.env = StrictEnvironment(context=c.input_dict)

    # Entrypoint into
    # from cookiecutter.parser.parse_provider import get_providers
    # c.providers = get_providers(c)

    if not c.context_key:
        # Set as first key in context
        c.context_key = next(iter(c.input_dict))

    if '_template' in c.input_dict[c.context_key]:
        # Normal case where '_template' is set in the context in `main`
        with work_in(c.input_dict[c.context_key]['_template']):
            return parse_context(c, m, s)
    else:
        # Case where prompt is being called directly as is the case with an operator
        return parse_context(c, m, s)


if __name__ == '__main__':
    print()
