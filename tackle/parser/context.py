# -*- coding: utf-8 -*-

"""Parser for the general context without generic logic."""
import os
import logging
from collections import OrderedDict
from jinja2.exceptions import UndefinedError
from tackle.render import render_variable
from tackle.utils.context_manager import work_in
from tackle.utils.reader import read_config_file, apply_overwrites_to_inputs
from tackle.render.environment import StrictEnvironment
from tackle.exceptions import UndefinedVariableInTemplate
from tackle.parser.prompts import prompt_list, prompt_str, read_user_dict
from tackle.parser.hooks import parse_hook
from tackle.parser.providers import get_providers

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context, Mode, Source, Settings

logger = logging.getLogger(__name__)


def parse_context(context: 'Context', mode: 'Mode', source: 'Source'):
    """Parse the context and iterate over values.

    :param dict context: Source for field names and sample values.
    :param env: Jinja environment to render values with.
    :param context_key: The key to insert all the outputs under in the context dict.
    :param no_input: Prompt the user at command line for manual configuration.
    :param existing_context: A dictionary of values to use during rendering.
    :return: cc_dict
    """
    for key, raw in context.input_dict[context.context_key].items():
        context.key = key
        # context.raw = raw
        if mode.rerun and context.key in context.override_inputs:
            # If there is a rerun dictionary then insert it in output and proceed.
            context.output_dict[key] = context.override_inputs[key]
            continue
        if key.startswith(u'_') and not key.startswith('__'):
            context.output_dict[key] = raw
            continue
        elif key.startswith('__'):
            context.output_dict[key] = render_variable(context, raw)
            continue

        if key in context.overwrite_inputs:
            context.output_dict[key] = context.overwrite_inputs[key]
            continue

        try:
            if isinstance(raw, bool):
                # Simply set the variable - perhaps later make this a choice
                context.output_dict[key] = raw
            if isinstance(raw, list):
                # We are dealing with a choice variable
                context.output_dict[key] = prompt_list(context, mode, raw)
            elif isinstance(raw, str):
                # We are dealing with a regular variable
                context.output_dict[key] = prompt_str(context, mode, raw)

            elif isinstance(raw, dict):
                # dict parsing logic
                if 'type' not in raw:
                    val = render_variable(context, raw)
                    if not mode.no_input:
                        val = read_user_dict(key, val)
                    context.output_dict[key] = val
                else:
                    # Main entrypoint into hook parsing logic
                    parse_hook(context, mode, source)

        except UndefinedError as err:
            if mode.record or mode.rerun:
                # Dump the output context
                pass

            msg = "Unable to render variable '{}'".format(key)
            raise UndefinedVariableInTemplate(msg, err, context.input_dict)

    return context


def prep_context(
    context: 'Context', mode: 'Mode', source: 'Source', settings: 'Settings'
):
    """
    Prompt user to enter values.

    Function sets the jinja environment and brings in extensions.
    """
    context.input_dict = OrderedDict([])
    obj = read_config_file(os.path.join(source.repo_dir, source.context_file))

    # Add the Python object to the context dictionary
    if not context.context_key:
        file_name = os.path.split(source.context_file)[1]
        file_stem = file_name.split('.')[0]
        context.input_dict[file_stem] = obj
    else:
        context.input_dict[context.context_key] = obj

    # Overwrite context variable defaults with the default context from the
    # user's global config, if available
    if settings.default_context:
        apply_overwrites_to_inputs(obj, settings.default_context)

    if context.overwrite_inputs:
        apply_overwrites_to_inputs(obj, context.overwrite_inputs)
    else:
        context.overwrite_inputs = OrderedDict()

    if not context.override_inputs:
        context.override_inputs = OrderedDict()

    # include template dir or url in the context dict
    context.input_dict[context.context_key]['_template'] = source.repo_dir

    logger.debug('Context generated is %s', context.input_dict)

    if not context.existing_context:
        context.output_dict = OrderedDict([])
    else:
        context.output_dict = OrderedDict(context.existing_context)

    context.env = StrictEnvironment(context=context.input_dict)

    # Entrypoint into
    get_providers(context, source, settings, mode)

    if not context.context_key:
        # Set as first key in context
        context.context_key = next(iter(context.input_dict))

    if '_template' in context.input_dict[context.context_key]:
        # Normal case where '_template' is set in the context in `main`
        with work_in(context.input_dict[context.context_key]['_template']):
            return parse_context(context, mode, source)
    else:
        # Case where prompt is being called directly as is the case with an hook
        return parse_context(context, mode, source)


if __name__ == '__main__':
    print()
