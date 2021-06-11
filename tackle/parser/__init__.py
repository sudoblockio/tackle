# -*- coding: utf-8 -*-

"""Context related items."""
import os
import yaml
import logging
from collections import OrderedDict

from tackle.parser.context import prep_context
from tackle.utils.files import load, dump

from tackle.exceptions import InvalidModeException
from pathlib import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Context, Settings, Providers

logger = logging.getLogger(__name__)


def _output_record(context: 'Context', settings: 'Settings'):
    if isinstance(context.record, bool):
        # Bool indicates dumping def
        dump(
            context.calling_directory,
            context.context_key + '.record',
            context.output_dict,
            settings.dump_output,
        )

    if isinstance(context.record, str):
        # Str indicates path to file to dump output to
        if context.record.startswith('/'):
            dump('/', context.record, context.output_dict, settings.dump_output)
        if os.path.exists(Path(context.record).parent):
            dump(os.curdir, context.record, context.output_dict, settings.dump_output)
        else:
            dump(
                context.calling_directory,
                context.record,
                context.output_dict,
                settings.dump_output,
            )


def _evaluate_rerun(rerun_path):
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
    settings: 'Settings',
    providers: 'Providers',
) -> OrderedDict:
    """Get output dict and entrypoint into broader parsing of context."""
    # _validate_context(context, mode)
    # _enrich_context(context, source)

    if context.replay:
        if isinstance(context.replay, bool):
            context.output_dict = load(
                settings.replay_dir, context.template_name, context.context_key
            )
            return  # noqa
        else:
            path, template_name = os.path.split(os.path.splitext(context.replay)[0])
            context.output_dict = load(path, template_name, context.context_key)
            return  # noqa

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
            context.override_inputs = _evaluate_rerun(context.rerun_path)
        if isinstance(context.rerun, bool):
            context.rerun_path = os.path.join(
                context.calling_directory,
                '.' + '.'.join([context.template_name, settings.rerun_file_suffix]),
            )
            context.override_inputs = _evaluate_rerun(context.rerun_path)

    # context_file_path = os.path.join(context.repo_dir, context.context_file)
    # logger.debug('context_file is %s', context_file_path)

    # Main entrypoint to parse the input.
    prep_context(context=context, settings=settings)

    if context.record:
        _output_record(context=context, settings=settings)
