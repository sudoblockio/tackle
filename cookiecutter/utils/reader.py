"""Generic reader for json, yaml, and hcl."""
import json
import os
from collections import OrderedDict

from cookiecutter.exceptions import ContextDecodingException

import hcl
import yaml
import logging

logger = logging.getLogger(__name__)


def read_config_file(file, file_extension=None):
    """Read files into objects."""
    if not file_extension:
        file_extension = file.split('.')[-1]

    if not os.path.exists(file):
        raise FileNotFoundError

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
        elif file_extension in ('yaml', 'yml', 'nukirc'):
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
