"""Helper functions used throughout Cookiecutter."""
import errno
import logging
import os
import shutil
import stat
import sys
import json
import yaml
import hcl
from _collections import OrderedDict

from cookiecutter.prompt import read_user_yes_no

logger = logging.getLogger(__name__)


def force_delete(func, path, exc_info):
    """Error handler for `shutil.rmtree()` equivalent to `rm -rf`.

    Usage: `shutil.rmtree(path, onerror=force_delete)`
    From stackoverflow.com/questions/1889597
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def rmtree(path):
    """Remove a directory and all its contents. Like rm -rf on Unix.

    :param path: A directory path.
    """
    shutil.rmtree(path, onerror=force_delete)


def make_sure_path_exists(path):
    """Ensure that a directory exists.

    :param path: A directory path.
    """
    logger.debug('Making sure path exists: %s', path)
    try:
        os.makedirs(path)
        logger.debug('Created directory at: %s', path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            return False
    return True


def make_executable(script_path):
    """Make `script_path` executable.

    :param script_path: The file to change
    """
    status = os.stat(script_path)
    os.chmod(script_path, status.st_mode | stat.S_IEXEC)


def prompt_and_delete(path, no_input=False):
    """
    Ask user if it's okay to delete the previously-downloaded file/directory.

    If yes, delete it. If no, checks to see if the old version should be
    reused. If yes, it's reused; otherwise, Cookiecutter exits.

    :param path: Previously downloaded zipfile.
    :param no_input: Suppress prompt to delete repo and just delete it.
    :return: True if the content was deleted
    """
    # Suppress prompt if called via API
    if no_input:
        ok_to_delete = True
    else:
        question = (
            "You've downloaded {} before. Is it okay to delete and re-download it?"
        ).format(path)

        ok_to_delete = read_user_yes_no(question, 'yes')

    if ok_to_delete:
        if os.path.isdir(path):
            rmtree(path)
        else:
            os.remove(path)
        return True
    else:
        ok_to_reuse = read_user_yes_no(
            "Do you want to re-use the existing version?", 'yes'
        )

        if ok_to_reuse:
            return False

        sys.exit()


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
            config = yaml.load(f, Loader=yaml.FullLoader)
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
