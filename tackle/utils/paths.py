"""Path related utils."""
import contextlib
import errno
import os
import shutil
import stat
import logging
import re

from tackle.exceptions import ContextFileNotFound

logger = logging.getLogger(__name__)

CONTEXT_FILE_DICT = {
    'cookiecutter': [
        'cookiecutter.json',
        'cookiecutter.yaml',
        'cookiecutter.yml',
        # 'cookiecutter.hcl',
    ],
    'tackle': [
        '.tackle.yaml',
        '.tackle.yml',
        '.tackle.json',
        '.tackle.hcl',
        'tackle.yaml',
        'tackle.yml',
        'tackle.json',
        # 'tackle.hcl',
    ],
}

ALL_VALID_CONTEXT_FILES = (
    CONTEXT_FILE_DICT['cookiecutter'] + CONTEXT_FILE_DICT['tackle']
)


def determine_tackle_generation(context_file: str) -> str:
    """Determine the tackle generation."""
    if context_file in CONTEXT_FILE_DICT['cookiecutter']:
        return 'cookiecutter'
    else:
        return 'tackle'


def listdir_absolute(directory, skip_paths=None):
    """Return and iterator of the absolute path."""
    if skip_paths is None:
        skip_paths = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if f not in skip_paths:
                yield os.path.abspath(os.path.join(dirpath, f))


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
    if os.path.islink(path):
        os.unlink(path)
    else:
        # Regular file
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


def expand_paths(paths: list) -> list:
    """Expand a list of paths."""
    output = []
    for i in paths:
        output.append(os.path.abspath(os.path.expanduser(os.path.expandvars(i))))
    return output


def expand_path(path: str) -> str:
    """Expand both environment variables and user home in the given path."""
    path = os.path.expandvars(path)
    path = os.path.expanduser(path)
    return path


def expand_abbreviations(template, abbreviations) -> str:
    """Expand abbreviations in a template name.

    :param template: The project template name.
    :param abbreviations: Abbreviation definitions.
    """
    if template in abbreviations:
        return abbreviations[template]

    # Split on colon. If there is no colon, rest will be empty
    # and prefix will be the whole template
    prefix, sep, rest = template.partition(':')
    if prefix in abbreviations:
        return abbreviations[prefix].format(rest)

    return template


def is_repo_url(value):
    """Return True if value is a repository URL."""
    REPO_REGEX = re.compile(
        r"""
    # something like git:// ssh:// file:// etc.
    ((((git|hg)\+)?(git|ssh|file|https?):(//)?)
     |                                      # or
     (\w+@[\w\.]+)                          # something like user@...
    )
    """,
        re.VERBOSE,
    )
    return bool(REPO_REGEX.match(value))


def is_file(value):
    """Return True if the input looks like a file."""
    FILE_REGEX = re.compile(
        r"""^.*\.(yaml|yml|json)$""",
        re.VERBOSE,
    )
    return bool(FILE_REGEX.match(value))


def is_multi_part_command(value):
    """Return True if the input looks like a file."""
    SPACE_REGEX = re.compile(
        r"""/\s/""",
        re.VERBOSE,
    )
    return bool(SPACE_REGEX.match(value))


# def is_tackle_project(value):
#     """Return True if the input looks like a file."""
#     repo_directory_exists = os.path.isdir(value)
#     if repo_directory_exists:
#         # Check for valid context files as default
#         for f in ALL_VALID_CONTEXT_FILES:
#             if os.path.isfile(os.path.join(value, f)):
#                 return True
#     return False


def repository_has_tackle_file(repo_directory: str, context_file=None):
    """
    Determine if `repo_directory` contains a valid context file. Acceptable choices
    are `tackle.yaml`, `tackle.yml`, `tackle.json`, `cookiecutter.json` in order of
    precedence.

    :param repo_directory: The candidate repository directory.
    :param context_file: eg. `tackle.yaml`.
    :return: The path to the context file
    """
    if context_file:
        # The supplied context file exists
        context_file = os.path.join(os.path.abspath(repo_directory), context_file)
        if os.path.isfile(context_file):
            return context_file
        else:
            raise ContextFileNotFound(
                f"Can't find supplied context_file at {context_file}"
            )

    repo_directory_exists = os.path.isdir(repo_directory)
    if repo_directory_exists:
        # Check for valid context files as default
        for f in ALL_VALID_CONTEXT_FILES:
            if os.path.isfile(os.path.join(repo_directory, f)):
                return f
    else:
        return None


@contextlib.contextmanager
def work_in(dirname=None):
    """Context manager version of os.chdir.

    When exited, returns to the working directory prior to entering.
    """
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)
