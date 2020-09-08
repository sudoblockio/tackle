"""Generic reader for json, yaml, and hcl."""
import json
import os
from collections import OrderedDict

import hcl
import yaml

from cookiecutter.utils import logger


def read_config_file(file):
    """Read files into objects."""
    file_extension = file.split('.')[-1]

    if not os.path.exists(file):
        raise FileNotFoundError

    logger.debug(
        'Using \"{}\" as input file and \"{}\" as file extension'.format(
            file, file_extension
        )
    )
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
