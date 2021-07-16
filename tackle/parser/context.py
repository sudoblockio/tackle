# -*- coding: utf-8 -*-

"""Parser for the general context without generic logic."""
import os
import logging
import yaml
from pathlib import Path
from jinja2.exceptions import UndefinedError
from tackle.render import render_variable
from tackle.utils.context_manager import work_in
from tackle.utils.files import load, dump

from tackle.exceptions import UndefinedVariableInTemplate, UnknownHookTypeException
from tackle.parser.prompts import prompt_list, prompt_str, read_user_dict
from tackle.parser.hooks import parse_hook

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context, Settings

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


# TODO: Break this function up
def prep_context(context: 'Context', settings: 'Settings'):
    """Prepare the context by setting some default values."""
    # Read config
    # obj = read_config_file(os.path.join(context.repo_dir, context.context_file))
    #
    # # Add the Python object to the context dictionary
    # if not context.context_key:
    #     file_name = os.path.split(context.context_file)[1]
    #     file_stem = file_name.split('.')[0]
    #     context.input_dict[file_stem] = obj
    # else:
    #     context.input_dict[context.context_key] = obj
    #
    # # Overwrite context variable defaults with the default context from the
    # # user's global config, if available
    # if settings.default_context:
    #     apply_overwrites_to_inputs(obj, settings.default_context)
    #
    # # Apply the overwrites/rides
    # # Strings are interpretted as pointers to files
    # if isinstance(context.overwrite_inputs, str):
    #     context.overwrite_inputs = read_config_file(context.overwrite_inputs)
    # if context.overwrite_inputs:
    #     apply_overwrites_to_inputs(obj, context.overwrite_inputs)
    # else:
    #     context.overwrite_inputs = {}
    #
    # # TODO: FIx the override logic in how it is interpreted by hooks
    # if not context.override_inputs:
    #     context.override_inputs = {}
    #
    # # include template dir or url in the context dict
    # context.input_dict[context.context_key]['_template'] = context.repo_dir
    #
    # logger.debug('Context generated is %s', context.input_dict)
    #
    # if not context.existing_context:
    #     context.output_dict = OrderedDict([])
    # else:
    #     context.output_dict = OrderedDict(context.existing_context)

    # Entrypoint into providers.py
    # get_providers(context, settings)
    #
    # with work_in(context.input_dict[context.context_key]['_template']):
    #     return parse_context(context)


def output_record(context: 'Context'):
    """Output a file that can be used to """
    pass


def evaluate_rerun(rerun_path):
    if os.path.exists(rerun_path):
        with open(rerun_path, 'r') as f:
            return yaml.safe_load(f)
    # else:
    #     if not context.record:
    #         print('No rerun file, will create record and use next time.')
    #         context.record = True


# def _enrich_context(context: 'Context', source: 'Source'):
#     if not context.context_key:
#         context.context_key = os.path.basename(source.context_file).split('.')[0]
#     if not context.calling_directory:
#         context.calling_directory = os.path.abspath(os.path.curdir)


# def _validate_context(context: 'Context', mode: 'Mode'):
#     if context.replay and len(context.overwrite_inputs) != 0:
#         err_msg = "You can not use both replay and extra_context at the same time."
#         raise InvalidModeException(err_msg)
#     if context.replay and context.rerun:
#         err_msg = "You can not use both replay and rerun at the same time."
#         raise InvalidModeException(err_msg)


def update_context(
        context: 'Context',
):
    """Get output dict and entrypoint into broader parsing of context."""
    # _validate_context(context, mode)
    # _enrich_context(context, source)

    if context.replay:
        if isinstance(context.replay, bool):
            context.output_dict = load(
                context.settings.replay_dir, context.template_name, context.context_key
            )
            return
        else:
            # path, template_name = os.path.split(os.path.splitext(context.replay)[0])
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
            context.override_inputs = evaluate_rerun(context.rerun_path)
        if isinstance(context.rerun, bool):
            context.rerun_path = os.path.join(
                context.calling_directory,
                '.' + '.'.join([context.template_name, context.settings.rerun_file_suffix]),
            )
            context.override_inputs = evaluate_rerun(context.rerun_path)

    TESTING = os.path.abspath('.')
    # Main entrypoint to parse the input.
    with work_in(context.repo_dir):
        parse_context(context)

    if context.record:
        if isinstance(context.record, bool):
            # Bool indicates dumping def
            dump(
                context.calling_directory,
                context.context_key + '.record',
                context.output_dict,
                context.settings.dump_output,
            )

        if isinstance(context.record, str):
            # Str indicates path to file to dump output to
            if context.record.startswith('/'):
                dump('/', context.record, context.output_dict, context.settings.dump_output)
            if os.path.exists(Path(context.record).parent):
                dump(os.curdir, context.record, context.output_dict, context.settings.dump_output)
            else:
                dump(
                    context.calling_directory,
                    context.record,
                    context.output_dict,
                    context.settings.dump_output,
                )
