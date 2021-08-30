"""Utilities mainly used in helping `modes` like replay and others."""
import json
from collections import OrderedDict
import hcl
import oyaml as yaml
import os
import logging

from tackle.exceptions import ContextDecodingException
from tackle.utils.paths import make_sure_path_exists

logger = logging.getLogger(__name__)


def get_file_name(replay_dir, template_name, suffix='yaml'):
    """Get the name of file."""
    suffix = '.' + suffix if not template_name.endswith('.' + suffix) else ''
    file_name = '{}{}'.format(template_name, suffix)
    return os.path.join(replay_dir, file_name)


def dump(output_dir, output_name, output_dict, dump_output='yaml'):
    """Write json data to file."""
    if not make_sure_path_exists(output_dir):
        raise IOError('Unable to create replay dir at {}'.format(output_dir))

    replay_file = get_file_name(output_dir, output_name, dump_output)

    if dump_output == 'json':
        with open(replay_file, 'w') as f:
            json.dump(output_dict, f, indent=2)
    if dump_output in ['yaml', 'yml']:
        with open(replay_file, 'w') as f:
            yaml.dump(output_dict, f, indent=2)


def load(replay_dir, template_name, context_key):
    """Read json data from file."""
    replay_file = get_file_name(replay_dir, template_name)

    with open(replay_file, 'r') as infile:
        context = yaml.load(infile, yaml.SafeLoader)

    if context_key not in context:
        raise ValueError('Context does not contain the context_key %s' % context_key)

    return context


def read_config_file(file, file_extension=None):
    """Read files into objects."""
    if not file_extension:
        file_extension = file.split('.')[-1]

    if not os.path.exists(file):
        raise FileNotFoundError(f"Can't find the file {file}.")

    logger.debug(
        'Using \"{}\" as input file and \"{}\" as file extension'.format(
            file, file_extension
        )
    )
    try:
        if file_extension == 'json':
            with open(file) as f:
                config = json.load(f, object_pairs_hook=OrderedDict)
            return config
        elif file_extension in ('yaml', 'yml', 'tacklerc'):
            with open(file, encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        elif file_extension == 'hcl':
            with open(file) as f:
                config = hcl.loads(f.read())
            return config
        else:
            raise ValueError(
                'Unable to parse file {}. Error: Unsupported extension (json/yaml only)'
                ''.format(file)
            )  # noqa

    except ValueError as e:
        # JSON decoding error.  Let's throw a new exception that is more
        # friendly for the developer or user.
        our_exc_message = (
            'JSON decoding error while loading "{0}".  Decoding'
            ' error details: "{1}"'.format(file, str(e))
        )
        raise ContextDecodingException(our_exc_message)


def apply_overwrites_to_inputs(input, overwrite_dict):
    """Modify the given context in place based on the overwrite_context."""
    for variable, overwrite in overwrite_dict.items():
        if variable not in input:
            # Do not include variables which are not used in the template
            continue

        context_value = input[variable]

        if isinstance(context_value, list):
            # We are dealing with a choice variable
            if overwrite in context_value:
                # This overwrite is actually valid for the given context
                # Let's set it as default (by definition first item in list)
                context_value.remove(overwrite)
                context_value.insert(0, overwrite)
        else:
            # Simply overwrite the value for this variable
            input[variable] = overwrite
