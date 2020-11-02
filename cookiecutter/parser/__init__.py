# -*- coding: utf-8 -*-

"""Context related items."""
import os
import yaml
import logging
from collections import OrderedDict

from cookiecutter.parser.parse_context import prep_context
from cookiecutter.parser.replay import load, dump
from cookiecutter.parser.generate import generate_context
from cookiecutter.exceptions import InvalidModeException
from pathlib import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cookiecutter.models import Context, Mode, Source
    from cookiecutter.configs import Settings

logger = logging.getLogger(__name__)


def _evaluate_rerun(rerun_path, m: 'Mode'):
    if os.path.exists(rerun_path):
        with open(rerun_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        print('No rerun file, will create record and use next time.')
        m.record = True  # noqa


def update_context(
    c: 'Context', s: 'Source', m: 'Mode', settings: 'Settings'
) -> OrderedDict:
    """Get output dict and entrypoint into broader parsing of context."""
    _validate_context(c, m)
    _enrich_context(c, s)

    if m.replay:
        if isinstance(m.replay, bool):
            c.output_dict = load(settings.replay_dir, s.template_name, c.context_key)
            return
        else:
            path, template_name = os.path.split(os.path.splitext(m.replay)[0])
            c.output_dict = load(path, template_name, c.context_key)
            return

    elif m.rerun:
        if isinstance(m.rerun, bool):
            rerun_path = os.path.join(
                c.calling_directory, '.' + '.'.join([s.template_name, 'rerun', 'yml'])
            )
            _evaluate_rerun(rerun_path, m)
        if isinstance(m.rerun, str):
            rerun_path = m.rerun
            _evaluate_rerun(rerun_path, m)

    else:
        context_file_path = os.path.join(s.repo_dir, s.context_file)
        logger.debug('context_file is %s', context_file_path)

        c.input_dict = generate_context(
            context_file=context_file_path,
            default_context=settings.default_context,
            extra_context=c.extra_context,
            context_key=c.context_key,
        )

        # include template dir or url in the context dict
        c.input_dict[c.context_key]['_template'] = s.repo_dir
        # include output+dir in the context dict
        c.input_dict[c.context_key]['_output_dir'] = os.path.abspath(m.output_dir)

        # prompt the user to manually configure at the command line.pyth
        # except when 'no-input' flag is set
        c = prep_context(c=c, mode=m, settings=settings)

        if m.record:
            if isinstance(m.record, bool):
                # Bool indicates
                dump(c.calling_directory, s.template_name, c.output_dict, c.context_key)
            if isinstance(m.record, str):
                # Str indicates path to file to dump output to
                if m.record.startswith('/'):
                    dump('/', m.record, c.output_dict, c.context_key)
                if os.path.exists(Path(m.record).parent):
                    dump(os.curdir, m.record, c.output_dict, c.context_key)
                else:
                    dump(c.calling_directory, m.record, c.output_dict, c.context_key)


def _output_record(c: 'Context', m: 'Mode', s: 'Settings'):
    if isinstance(m.record, bool):
        # Bool indicates
        dump(c.calling_directory, s.template_name, c.output_dict, c.context_key)
    if isinstance(m.record, str):
        # Str indicates path to file to dump output to
        dump(s.replay_dir, s.template_name, c.output_dict, c.context_key)


def _enrich_context(c: 'Context', s: 'Source'):
    if not c.context_key:
        c.context_key = os.path.basename(s.context_file).split('.')[0]

    if not c.calling_directory:
        c.calling_directory = os.path.abspath(os.path.curdir)


def _validate_context(c: 'Context', m: 'Mode'):
    if m.replay and c.extra_context is not None:
        err_msg = "You can not use both replay and extra_context at the same time."
        raise InvalidModeException(err_msg)
    if m.replay and m.rerun:
        err_msg = "You can not use both replay and rerun at the same time."
        raise InvalidModeException(err_msg)
