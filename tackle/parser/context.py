# -*- coding: utf-8 -*-

"""Parser for the general context without generic logic."""
import os
import logging
import yaml
from collections import OrderedDict
from jinja2.exceptions import UndefinedError
from tackle.render import render_variable
from tackle.utils.context_manager import work_in
from tackle.utils.reader import read_config_file, apply_overwrites_to_inputs
from tackle.exceptions import UndefinedVariableInTemplate, UnknownHookTypeException
from tackle.parser.prompts import prompt_list, prompt_str, read_user_dict
from tackle.parser.hooks import parse_hook
from tackle.parser.providers import get_providers

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context, Mode, Source, Settings

logger = logging.getLogger(__name__)


# TODO: Fix this per rerun logic issue
def dump_rerun_on_error(context: 'Context', mode: 'Mode'):
    """Dump the context on failure."""
    if mode.record or mode.rerun:
        # Dump the output context
        print(f"Writing rerun file to {context.rerun_path}")
        with open(context.rerun_path, 'w') as f:
            yaml.dump(dict(context.output_dict), f)


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
        # if context.key in context.override_inputs:
        #     # If there is a rerun dictionary then insert it in output and proceed.
        #     context.output_dict[key] = context.override_inputs[key]
        #     continue
        if key.startswith(u'_') and not key.startswith('__'):
            # Single underscore denotes unrendered value
            context.output_dict[key] = raw
            continue
        elif key.startswith('__'):
            # Double underscore denotes rendered value
            context.output_dict[key] = render_variable(context, raw)
            continue

        if context.overwrite_inputs:
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
            dump_rerun_on_error(context, mode)
            msg = "Unable to render variable '{}'".format(key)
            raise UndefinedVariableInTemplate(msg, err, context.input_dict)
        except UnknownHookTypeException as err:
            dump_rerun_on_error(context, mode)
            raise UnknownHookTypeException(err)

    return context

# TODO: Break this function up
def prep_context(
    context: 'Context', mode: 'Mode', source: 'Source', settings: 'Settings'
):
    """Prepare the context by setting some default values."""
    # Read config
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

    # Apply the overwrites/rides
    # Strings are interpretted as pointers to files
    if isinstance(context.overwrite_inputs, str):
        context.overwrite_inputs = read_config_file(context.overwrite_inputs)
    if context.overwrite_inputs:
        apply_overwrites_to_inputs(obj, context.overwrite_inputs)
    else:
        context.overwrite_inputs = {}

    # TODO: FIx the override logic in how it is interpreted by hooks
    if not context.override_inputs:
        context.override_inputs = {}

    # include template dir or url in the context dict
    context.input_dict[context.context_key]['_template'] = source.repo_dir

    logger.debug('Context generated is %s', context.input_dict)

    if not context.existing_context:
        context.output_dict = OrderedDict([])
    else:
        context.output_dict = OrderedDict(context.existing_context)

    # Entrypoint into providers.py
    get_providers(context, source, settings, mode)

    with work_in(context.input_dict[context.context_key]['_template']):
        return parse_context(context, mode, source)
