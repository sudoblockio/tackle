import csv
import os
import platform
from typing import TYPE_CHECKING

from xdg import (
    xdg_cache_home,
    xdg_config_dirs,
    xdg_config_home,
    xdg_data_dirs,
    xdg_data_home,
    xdg_runtime_dir,
    xdg_state_home,
)

from tackle.settings import settings

if TYPE_CHECKING:
    from tackle.models import Context


def get_linux_distribution():
    """Return the equivalent of lsb_release -a."""
    if platform.system() == 'Linux':
        RELEASE_DATA = {}
        with open("/etc/os-release") as f:
            reader = csv.reader(f, delimiter="=")
            for row in reader:
                if row:
                    RELEASE_DATA[row[0]] = row[1]
        if RELEASE_DATA["ID"] in ["debian", "raspbian"]:
            with open("/etc/debian_version") as f:
                DEBIAN_VERSION = f.readline().strip()
            major_version = DEBIAN_VERSION.split(".")[0]
            version_split = RELEASE_DATA["VERSION"].split(" ", maxsplit=1)
            if version_split[0] == major_version:
                # Just major version shown, replace it with the full version
                RELEASE_DATA["VERSION"] = " ".join([DEBIAN_VERSION] + version_split[1:])
        return "{} {}".format(RELEASE_DATA["NAME"], RELEASE_DATA["VERSION"])
    else:
        return None


def _cwd():
    return os.getcwd()


def _home_dir():
    return os.path.expanduser('~')


def _system():
    return platform.system()


def _platform():
    return platform.platform()


def _release():
    return platform.release()


def _version():
    return platform.version()


def _processor():
    return platform.processor()


def _architecture():
    return platform.architecture()


def _tackle_dir():
    return settings.tackle_dir


def _providers_dir():
    return settings.providers_dir


def _calling_directory(context: 'Context'):
    return context.path.calling.calling_directory


def _calling_file(context: 'Context'):
    return context.path.calling.file


def _current_file(context: 'Context'):
    return context.source.file


def _current_directory(context: 'Context'):
    return context.source.directory


def _hooks_directory(context: 'Context'):
    return context.source.hooks_dir


def _this(context: 'Context'):
    return context.data.public


def _public_data(context: 'Context'):
    return context.data.public


def _private_data(context: 'Context'):
    return context.data.private


def _temporary_data(context: 'Context'):
    return context.data.temporary


def _existing_data(context: 'Context'):
    return context.data.existing


def _key_path(context: 'Context'):
    return context.key_path


def _key_path_block(context: 'Context'):
    return context.key_path_block


def _xdg_cache_home():
    return xdg_cache_home()


def _xdg_config_dirs():
    return xdg_config_dirs()


def _xdg_config_home():
    return xdg_config_home()


def _xdg_data_dirs():
    return xdg_data_dirs()


def _xdg_data_home():
    return xdg_data_home()


def _xdg_runtime_dir():
    return xdg_runtime_dir()


def _xdg_state_home():
    return xdg_state_home()


special_variables = {
    'cwd': _cwd,
    'home_dir': _home_dir,
    'system': _system,
    'platform': _platform,
    'version': _version,
    'processor': _processor,
    'architecture': _architecture,
    'lsb_release': get_linux_distribution,
    'tackle_dir': _tackle_dir,
    'provider_dir': _providers_dir,
    'calling_directory': _calling_directory,
    'calling_file': _calling_file,
    'current_file': _current_file,
    'current_directory': _current_directory,
    'hooks_directory': _hooks_directory,
    'this': _this,
    'public_data': _public_data,
    'private_data': _private_data,
    'existing_data': _existing_data,
    'temporary_data': _temporary_data,
    'key_path': _key_path,
    'key_path_block': _key_path_block,
    'xdg_cache_home': _xdg_cache_home,
    'xdg_config_dirs': _xdg_config_dirs,
    'xdg_config_home': _xdg_config_home,
    'xdg_data_dirs': _xdg_data_dirs,
    'xdg_data_home': _xdg_data_home,
    'xdg_runtime_dir': _xdg_runtime_dir,
    'xdg_state_home': _xdg_state_home,
}
