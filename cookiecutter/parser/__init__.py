# -*- coding: utf-8 -*-

"""Context related items."""
import os
import yaml
import logging
from collections import OrderedDict

from cookiecutter.parser.context import prep_context
from cookiecutter.utils.files import load, dump

# from cookiecutter.parser.prepare import prepare_context
from cookiecutter.exceptions import InvalidModeException
from pathlib import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cookiecutter.models import Context, Mode, Source, Settings

logger = logging.getLogger(__name__)


def update_context(
    c: 'Context', s: 'Source', m: 'Mode', settings: 'Settings'
) -> OrderedDict:
    """Get output dict and entrypoint into broader parsing of context."""
    _validate_context(c, m)
    _enrich_context(c, s)

    if m.replay:
        if isinstance(m.replay, bool):
            c.output_dict = load(settings.replay_dir, s.template_name, c.context_key)
            return  # noqa
        else:
            path, template_name = os.path.split(os.path.splitext(m.replay)[0])
            c.output_dict = load(path, template_name, c.context_key)
            return  # noqa

    if m.rerun:
        # Rerun will first try to read an existing rerun file and then load it into
        # the override input dict
        if isinstance(m.rerun, str):
            rerun_path = m.rerun
            c.override_inputs = _evaluate_rerun(rerun_path, m)
        if isinstance(m.rerun, bool):
            rerun_path = os.path.join(
                c.calling_directory,
                '.' + '.'.join([s.template_name, settings.rerun_file_suffix]),
            )
            c.override_inputs = _evaluate_rerun(rerun_path, m)

    context_file_path = os.path.join(s.repo_dir, s.context_file)
    logger.debug('context_file is %s', context_file_path)

    # prepare_context(c=c, s=s, settings=settings)
    # update_providers(c=c, s=s, settings=settings)

    # Main entrypoint to parse the input.
    prep_context(c=c, m=m, s=s, settings=settings)

    if m.record:
        _output_record(c=c, m=m, settings=settings)


def _output_record(c: 'Context', m: 'Mode', settings: 'Settings'):
    if isinstance(m.record, bool):
        # Bool indicates dumping def
        dump(c.calling_directory, c.context_key + '.record', c.output_dict, settings)

    if isinstance(m.record, str):
        # Str indicates path to file to dump output to
        if m.record.startswith('/'):
            dump('/', m.record, c.output_dict, settings)
        if os.path.exists(Path(m.record).parent):
            dump(os.curdir, m.record, c.output_dict, settings)
        else:
            dump(c.calling_directory, m.record, c.output_dict, settings)


def _evaluate_rerun(rerun_path, m: 'Mode'):
    if os.path.exists(rerun_path):
        with open(rerun_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        print('No rerun file, will create record and use next time.')
        m.record = True


def _enrich_context(c: 'Context', s: 'Source'):
    if not c.context_key:
        c.context_key = os.path.basename(s.context_file).split('.')[0]
    if not c.calling_directory:
        c.calling_directory = os.path.abspath(os.path.curdir)


def _validate_context(c: 'Context', m: 'Mode'):
    if m.replay and c.overwrite_inputs is not None:
        err_msg = "You can not use both replay and extra_context at the same time."
        raise InvalidModeException(err_msg)
    if m.replay and m.rerun:
        err_msg = "You can not use both replay and rerun at the same time."
        raise InvalidModeException(err_msg)
