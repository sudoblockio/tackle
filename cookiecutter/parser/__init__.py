"""Context related items."""
import os
import logging
from collections import OrderedDict

from cookiecutter.parser.parse_context import prep_context
from cookiecutter.replay import load, dump
from cookiecutter.parser.generate import generate_context

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cookiecutter.models import Context, Mode, Source
    from cookiecutter.configs import Settings

# from cookiecutter.model import Context, Mode, Source
# from cookiecutter.configs.config_base import Settings


logger = logging.getLogger(__name__)


def get_output(
    c: 'Context', s: 'Source', m: 'Mode', settings: 'Settings'
) -> OrderedDict:
    """Get output dict and entrypoint into broader parsing of context."""
    if not c.context_key:
        c.context_key = os.path.basename(s.context_file).split('.')[0]

    if m.replay:
        if isinstance(m.replay, bool):
            return load(settings.replay_dir, s.template_name, c.context_key)
        else:
            path, template_name = os.path.split(os.path.splitext(m.replay)[0])
            return load(path, template_name, c.context_key)

    elif m.rerun:
        pass

    else:
        context_file_path = os.path.join(s.repo_dir, s.context_file)
        # TODO Inspect... ^^
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
        # c.input_dict[c.context_key] = prep_context(c=c, mode=m, settings=settings)
        c = prep_context(c=c, mode=m, settings=settings)

        dump(settings.replay_dir, s.template_name, c.input_dict, c.context_key)


# def generate_context(
#         repo_dir: str,
#         context_key,
# ):
#     template_name = os.path.basename(os.path.abspath(repo_dir))
#     if not context_key:
#         context_key = os.path.basename(context_file).split('.')[0]
#
#     if replay:
#         if isinstance(replay, bool):
#             context = load(settings.replay_dir, template_name, context_key)
#         else:
#             path, template_name = os.path.split(os.path.splitext(replay)[0])
#             context = load(path, template_name, context_key)
#
#     else:
#         context_file_path = os.path.join(repo_dir, context_file)
#         logger.debug('context_file is %s', context_file_path)
#
#         context = generate_context(
#             context_file=context_file_path,
#             default_context=settings.default_context,
#             extra_context=extra_context,
#             context_key=context_key,
#         )
#
#         # include template dir or url in the context dict
#         context[context_key]['_template'] = repo_dir
#         # include output+dir in the context dict
#         context[context_key]['_output_dir'] = os.path.abspath(output_dir)
#
#         # prompt the user to manually configure at the command line.pyth
#         # except when 'no-input' flag is set
#         context[context_key] = prompt_for_config(
#             context, context_key, existing_context, mode
#         )
#
#         dump(settings.replay_dir, template_name, context, context_key)
