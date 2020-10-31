# -*- coding: utf-8 -*-

"""Parser for the general context without generic logic."""
from collections import OrderedDict
from jinja2.exceptions import UndefinedError
from cookiecutter.render import render_variable
from cookiecutter.utils.context_manager import work_in
from cookiecutter.render.environment import StrictEnvironment
from cookiecutter.exceptions import UndefinedVariableInTemplate
from cookiecutter.parser.prompts import prompt_list, prompt_str, read_user_dict
from cookiecutter.parser.parse_hook import parse_hook

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cookiecutter.models import Context, Mode
    from cookiecutter.configs import Settings

# from cookiecutter.models import Context, Mode
# from cookiecutter.configs.config_base import Settings

# context, env, cc_dict, context_key, mode: Mode = Field()):


def parse_context(c: 'Context', m: 'Mode', s: 'Settings'):
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
        if key.startswith(u'_') and not key.startswith('__'):
            c.output_dict[key] = raw
            continue
        elif key.startswith('__'):
            c.output_dict[key] = render_variable(c, raw)
            continue

        try:
            if isinstance(raw, list):
                # We are dealing with a choice variable
                c.output_dict[key] = prompt_list(c, m, raw)
            elif isinstance(raw, str):
                # We are dealing with a regular variable
                c.output_dict[key] = prompt_str(c, m, raw)
                # val = render_variable(c, raw)
                #
                # if not no_input:
                #     val = prompt_str(c, m, raw)
                #
                # c.output_dict[key] = val

            elif isinstance(raw, dict):
                # dict parsing logic
                if 'type' not in raw:
                    val = render_variable(c, raw)
                    if not m.no_input:
                        val = read_user_dict(key, val)
                    c.output_dict[key] = val
                else:
                    parse_hook(c, m, s)

        except UndefinedError as err:
            msg = "Unable to render variable '{}'".format(key)
            raise UndefinedVariableInTemplate(msg, err, c.input_dict)

    return c


def prep_context(
    c: 'Context', mode: 'Mode', settings: 'Settings',
):
    """
    Prompt user to enter values.

    Function sets the jinja environment and brings in extensions.

    :param dict c: Source for field names and sample values.
    :param no_input: Prompt the user at command line for manual configuration.
    :param context_key: The key to insert all the outputs under in the context dict.
    :param existing_context: A dictionary of values to use during rendering.
    """
    if not c.existing_context:
        c.output_dict = OrderedDict([])
    else:
        c.output_dict = OrderedDict(c.existing_context)

    c.env = StrictEnvironment(context=c.input_dict)

    if not c.context_key:
        # Set as first key in context
        c.context_key = next(iter(c.input_dict))

    if '_template' in c.input_dict[c.context_key]:
        # Normal case where '_template' is set in the context in `main`
        with work_in(c.input_dict[c.context_key]['_template']):
            return parse_context(c, mode, settings)
    else:
        # Case where prompt is being called directly as is the case with an operator
        return parse_context(c, mode, settings)
