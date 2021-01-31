"""Path related utils."""
import errno
import os
import shutil
import stat
import logging

logger = logging.getLogger(__name__)


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
