"""Utilities mainly used in helping `modes` like replay and others."""
import json
import logging
import os

from ruyaml import YAML
from ruyaml.composer import ComposerError
from ruyaml.constructor import ConstructorError
from ruyaml.parser import ParserError

from tackle import exceptions
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
        yaml = YAML()
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)
        with open(replay_file, 'w') as f:
            yaml.dump(output_dict, f)


def read_config_file(file, file_extension=None):
    """Read files into objects."""
    if not file_extension:
        file_extension = file.split('.')[-1]

    if not os.path.exists(file):
        raise exceptions.TackleFileNotFoundError(
            f"Can't find the file {file}."
        ) from None

    logger.debug(
        'Using \"{}\" as input file and \"{}\" as file extension'.format(
            file, file_extension
        )
    )
    try:
        if file_extension == 'json':
            with open(file) as f:
                config = json.load(f)
            return config
        elif file_extension in ('yaml', 'yml'):
            # Try normal and then for documents that will output as list
            yaml = YAML(typ="safe")
            try:
                with open(file, encoding='utf-8') as f:
                    config = yaml.load(f)
                return config
            except ComposerError:
                output = []
                with open(file, encoding='utf-8') as f:
                    for doc in yaml.load_all(f.read()):
                        output.append(doc)
                return output
            except ConstructorError as e:
                raise exceptions.FileLoadingException(
                    f"Error loading file={file}\n{e}\nLikely due to unquoted template "
                    "variable.\nie var: {{foo}}} | not var: '{{foo}}'"
                ) from None
            except ParserError as e:
                raise exceptions.FileLoadingException(
                    f"Error loading file={file}\n{e}",
                ) from None
        elif file_extension == 'toml':
            try:
                from tomli import load as toml_load
            except ModuleNotFoundError:
                from tomllib import load as toml_load
            # TODO: Catch these errors
            with open(file, 'rb') as f:
                data = toml_load(f)
            return data

        else:
            raise exceptions.UnsupportedBaseFileTypeException(
                'Unable to parse file {}. Error: Unsupported extension (json/yaml only)'
                ''.format(file)
            )  # noqa

    except ValueError as e:
        # decoding error
        message = f'Error while loading file=`{file}`. \n' f'Details: "{str(e)}"'
        raise exceptions.FileLoadingException(message) from None


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
