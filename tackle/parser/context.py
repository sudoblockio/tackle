# -*- coding: utf-8 -*-

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
from tackle.parser.prompts import prompt_list, prompt_str, read_user_dict
from tackle.parser.hooks import parse_hook

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context

logger = logging.getLogger(__name__)


# TODO: Fix this per rerun logic issue
def dump_rerun_on_error(context: 'Context'):
    """Dump the context on failure."""
    if context.record or context.rerun:
        # Dump the output context
        print(f"Writing rerun file to {context.rerun_path}")
        with open(context.rerun_path, 'w') as f:
            yaml.dump(dict(context.output_dict), f)


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


def evaluate_rerun(context):
    """Return file or if file does not exist, set record to be true."""
    if os.path.exists(context.rerun_path):
        with open(context.rerun_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        if not context.record:
            print('No rerun file, will create record and use next time.')
            context.record = True


def update_context(
    context: 'Context',
):
    """Get output dict and entrypoint into broader parsing of context."""
    if context.replay:
        if isinstance(context.replay, bool):
            context.output_dict = load(
                context.settings.replay_dir, context.template_name, context.context_key
            )
            return
        else:
            # TODO: fix
            path, template_name = os.path.split(os.path.splitext(context.replay)[0])
            context.output_dict = load(path, template_name, context.context_key)
            return

    if context.rerun:
        # Rerun will first try to read an existing rerun file and then load it into
        # the override input dict
        if isinstance(context.rerun, str):
            context.rerun_path = context.rerun
            # TODO: Bug right now where each time it tries to pull in the rerun file
            #  for embedded tackle calls when this is something that should be done
            #  once at the beginning of the execution. Doesn't matter if we move it
            #  around the main function call as it will be called twice regardless
            #  unless the function call is aware of which context (the calling context)
            #  or a subprocess context. Detecting based on calling dir won't work.
            # if os.path.abspath(os.path.curdir) == context.calling_directory:
            context.override_inputs = evaluate_rerun(context)
        if isinstance(context.rerun, bool):
            context.rerun_path = os.path.join(
                os.curdir,
                '.'
                + '.'.join([context.template_name, context.settings.rerun_file_suffix]),
            )
            context.override_inputs = evaluate_rerun(context)

    # Main entrypoint to parse the input.
    with work_in(context.repo_dir):
        parse_context(context)

    if context.record:
        if isinstance(context.record, bool):
            # Bool indicates dumping def
            dump(
                os.curdir,
                context.context_key + '.record',
                context.output_dict,
                context.settings.dump_output,
            )

        if isinstance(context.record, str):
            # Str indicates path to file to dump output to
            if context.record.startswith('/'):
                dump(
                    '/',
                    context.record,
                    context.output_dict,
                    context.settings.dump_output,
                )
            if os.path.exists(Path(context.record).parent):
                dump(
                    os.curdir,
                    context.record,
                    context.output_dict,
                    context.settings.dump_output,
                )
            else:
                dump(
                    context.calling_directory,
                    context.record,
                    context.output_dict,
                    context.settings.dump_output,
                )
