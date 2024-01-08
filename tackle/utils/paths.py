"""Path related utils."""
import contextlib
import errno
import logging
import os
import re
import shutil
import stat
from typing import TYPE_CHECKING, Optional

from tackle import exceptions

if TYPE_CHECKING:
    from tackle.context import Context

logger = logging.getLogger(__name__)

DEFAULT_TACKLE_FILES = {
    '.tackle.yaml',
    '.tackle.yml',
    '.tackle.json',
    '.tackle.toml',
    'tackle.yaml',
    'tackle.yml',
    'tackle.json',
    'tackle.toml',
}


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


def is_repo_url(value) -> bool:
    """
    Return True if value is a repository URL. Also checks if it is of the form
    org/repo ie robcxyz/tackle-demos and checks if that is a local directory before
    returning true.
    """
    REPO_REGEX = re.compile(
        r"""
    # something like git:// ssh:// file:// etc.
    ((((git|hg)\+)?(git|ssh|file|https?):(//)?)
     |
     (^(github.com|gitlab.com)+\/[\w,\-,\_]+\/[\w,\-,\_]+$)
    )
    """,
        re.VERBOSE,
    )
    if not bool(REPO_REGEX.match(value)):
        # We also need to catch refs of type robcxyz/tackle-demo but need to first see
        # if the path
        REPO_REGEX = re.compile(
            r"""^[\w,\-,\_]+\/[\w,\-,\_]+$""",
            re.VERBOSE,
        )
        if bool(REPO_REGEX.match(value)):
            if os.path.exists(value):
                return False
            else:
                return True
        else:
            return False

    return True
    # return bool(REPO_REGEX.match(value))


DEFAULT_TACKLE_FILES = {
    '.tackle.yaml',
    '.tackle.yml',
    '.tackle.json',
    '.tackle.toml',
    'tackle.yaml',
    'tackle.yml',
    'tackle.json',
    'tackle.toml',
}

DEFAULT_HOOKS_DIRECTORIES = {
    'hooks',
    '.hooks',
}


def find_hooks_directory_in_dir(directory: str) -> str:
    for i in os.scandir(directory):
        if i.is_dir() and i.name in DEFAULT_HOOKS_DIRECTORIES:
            return os.path.abspath(os.path.join(directory, i))


def find_tackle_file_in_dir(directory: str) -> str:
    """Return the path to a tackle file if it exists in a dir."""
    for i in os.scandir(directory):
        if i.is_file() and i.name in DEFAULT_TACKLE_FILES:
            return os.path.abspath(os.path.join(directory, i.name))


def find_tackle_base_in_parent_dir(
    directory: str,
) -> Optional[str]:
    """
    Recursively search in parent directories for a tackle base which is defined as
     a directory with either a tackle file or a hooks directory.
    """
    hooks_directory = find_hooks_directory_in_dir(directory=directory)
    if hooks_directory is not None:
        return directory
    tackle_file = find_tackle_file_in_dir(directory=directory)
    if tackle_file is not None:
        return directory

    if os.path.abspath(directory) == '/':
        return None
    return find_tackle_base_in_parent_dir(
        directory=os.path.dirname(os.path.abspath(directory)),
    )


def find_tackle_base_in_parent_dir_with_exception(
    context: 'Context',
    directory: str,
) -> str:
    """Call find_tackle_base_in_parent_dir and raise if no base is in parent."""
    base = find_tackle_base_in_parent_dir(directory=directory)
    if base is None:
        targets = list(DEFAULT_TACKLE_FILES) + list(DEFAULT_HOOKS_DIRECTORIES)
        raise exceptions.UnknownSourceException(
            f'The `find_in_parent` argument was specified and no valid tackle base'
            f' was detected, ie a directory with a valid tackle file or hooks'
            f' directory which is one of {" ,".join(targets)}',
            context=context,
        )
    return base


def find_tests_base_dir(directory: str) -> str | None:
    """Find the base dir of the parent test(s) directory."""
    # Normalize the path
    norm_dir = os.path.normpath(directory)

    # Split the path into parts
    path_split = norm_dir.split(os.sep)

    # Handle the root slash or drive letter
    if os.name == 'nt':  # Windows
        # Ensure the drive letter is preserved
        if norm_dir.startswith("\\\\"):  # UNC path
            root = "\\\\" + path_split[0]
            path_split = [root] + path_split[2:]
        else:
            path_split[0] += os.sep
    else:  # Unix-like
        if norm_dir.startswith(os.sep):
            path_split = [os.sep] + path_split[1:]

    # Iterate in reverse to find 'test' or 'tests'
    for i, v in enumerate(reversed(path_split)):
        if v == 'test' or v == 'tests':
            # Return the path index
            return os.path.join(*path_split[: len(path_split) - 1 - i])


def find_hooks_dir_from_tests(directory: str) -> str | None:
    """
    Super hacky way to determine if we are running tackle from a tests directory that is
     not a native provider
    """
    test_base = find_tests_base_dir(directory)
    if test_base is None:
        return
    # Check if native provider
    if os.path.isfile(os.path.join(test_base, '..', '.native')):
        return
    # Check if we are in tackle/tests/* dir
    base_dir_contents = os.listdir(test_base)
    if 'tackle' in base_dir_contents:
        if os.path.isfile(os.path.join(test_base, 'tackle', 'parser.py')):
            return
    # Return hooks dir
    if 'hooks' in base_dir_contents:
        return os.path.join(test_base, 'hooks')
    if '.hooks' in base_dir_contents:
        return os.path.join(test_base, '.hooks')


def is_directory_with_tackle(directory: str) -> bool:
    """Return true if directory."""
    if not os.path.isdir(directory):
        return False
    for i in os.scandir(directory):
        if i.is_dir() and i.name in DEFAULT_HOOKS_DIRECTORIES:
            return True
        if i.is_file() and i.name in DEFAULT_TACKLE_FILES:
            return True
    return False


def is_file(value: str, directory: Optional[str]) -> bool:
    """Return True if the input looks like a file."""
    FILE_REGEX = re.compile(
        r"""^.*\.(yaml|yml|json|toml)$""",
        re.VERBOSE,
    )
    if bool(FILE_REGEX.match(value)):
        if directory is not None:
            value = os.path.join(directory, value)
        return os.path.isfile(value)
    else:
        return False


# def repository_has_tackle_file(repo_directory: str, context_file=None):
#     """
#     Determine if `repo_directory` contains a valid context file. Acceptable choices
#     are `tackle.yaml`, `tackle.yml`, `tackle.json`, `cookiecutter.json` in order of
#     precedence.
#
#     :param repo_directory: The candidate repository directory.
#     :param context_file: eg. `tackle.yaml`.
#     :return: The path to the context file
#     """
#     if context_file:
#         # The supplied context file exists
#         context_file = os.path.join(os.path.abspath(repo_directory), context_file)
#         if os.path.isfile(context_file):
#             return context_file
#         else:
#             raise exceptions.ContextFileNotFound(
#                 f"Can't find supplied context_file at {context_file}"
#             )
#
#     repo_directory_exists = os.path.isdir(repo_directory)
#     if repo_directory_exists:
#         # Check for valid context files as default
#         for f in TACKLE_BASE_ITEMS:
#             if os.path.isfile(os.path.join(repo_directory, f)):
#                 return f
#     else:
#         return None


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
