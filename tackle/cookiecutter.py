"""Parser for the general context without generic logic."""
import os
import logging
import yaml
from pathlib import Path
from jinja2.exceptions import UndefinedError
from tackle.render import render_variable
from tackle.utils.paths import work_in
from tackle.utils.files import load, dump

from tackle.exceptions import UndefinedVariableInTemplate, UnknownHookTypeException
from tackle.prompts import prompt_list, prompt_str, read_user_dict
from tackle.hooks import parse_hook
from tackle.settings import settings

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context

logger = logging.getLogger(__name__)

# TODO: Move to utils
# TODO: Fix this per rerun logic issue
def dump_rerun_on_error(context: 'Context'):
    """Dump the context on failure."""
    if context.record or context.rerun:
        # Dump the output context
        print(f"Writing rerun file to {context.rerun_path}")
        with open(context.rerun_path, 'w') as f:
            yaml.dump(dict(context.output_dict), f)


# TODO: RF to parse_key()
def parse_context(context: 'Context'):
    """Parse the context based on the key type and iterate over values."""
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
                context.output_dict[key] = prompt_list(context, raw)
            elif isinstance(raw, str):
                # We are dealing with a regular variable
                context.output_dict[key] = prompt_str(context, raw)

            elif isinstance(raw, dict):
                # dict parsing logic
                if 'type' not in raw:
                    val = render_variable(context, raw)
                    if not context.no_input:
                        val = read_user_dict(key, val)
                    context.output_dict[key] = val
                else:
                    # Main entrypoint into hook parsing logic
                    parse_hook(context)

        except UndefinedError as err:
            dump_rerun_on_error(context)
            msg = "Unable to render variable '{}'".format(key)
            raise UndefinedVariableInTemplate(msg, err, context.input_dict)
        except UnknownHookTypeException as err:
            dump_rerun_on_error(context)
            raise UnknownHookTypeException(err)

    return context
