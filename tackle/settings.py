"""Settings initializer."""
from pydantic import BaseSettings, Field
from typing import Dict, List

import os
import logging
import pathlib

from tackle.utils.files import read_config_file
from tackle.exceptions import ConfigDoesNotExistException

from tackle.utils.paths import expand_path

logger = logging.getLogger(__name__)

USER_CONFIG_PATH = os.path.expanduser('~/.tacklerc')

DEFAULT_ABBREVIATIONS = {
    'gh': 'https://github.com/{0}.git',
    'gl': 'https://gitlab.com/{0}.git',
    'bb': 'https://bitbucket.org/{0}',
}


class Settings(BaseSettings):
    """Base settings that are immutable during main runtime."""

    tackle_dir: str = '~/.tackle'
    # settings_file: str = expand_path(os.path.join(tackle_dir, 'settings.yaml'))

    provider_dir: str = '~/.tackle/providers'
    config_path: str = expand_path(os.path.join(tackle_dir, 'settings.yaml'))
    replay_dir: str = expand_path(os.path.join(tackle_dir, 'replay'))

    rerun_file_suffix: str = 'rerun.yml'
    abbreviations: Dict = DEFAULT_ABBREVIATIONS
    default_context: Dict = None
    extra_providers: list = []
    dump_output: str = 'yaml'

    hook_keys: List[str] = None

    class Config:
        env_prefix = 'TACKLE_'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = "ignore"

    def __init__(self, **values: Dict):
        super().__init__(**values)
        if self.hook_keys is None:
            self.hook_keys = ['type', '<']

        # TODO: Test
        if os.path.exists(self.config_path):
            global_settings = read_config_file(self.config_path)
            for k, v in global_settings:
                setattr(self, k, v)

        if not os.path.isdir(self.provider_dir):
            pathlib.Path(self.provider_dir).mkdir(parents=True, exist_ok=True)

        # self.abbreviations.update(DEFAULT_ABBREVIATIONS)
        # self.tackle_dir = expand_path(self.tackle_dir)
        # self.replay_dir = expand_path(self.replay_dir)


settings = Settings()


# def get_settings(
#     config_file: str = None,
#     config: dict = None,
#     default_config: bool = False,
# ) -> 'Settings':
#     """
#     Return the user config as a dict.
#
#     If ``default_config`` is True, ignore ``config_file`` and return default
#     values for the config parameters.
#
#     If a path to a ``config_file`` is given, that is different from the default
#     location, load the user config from that.
#
#     Otherwise look up the config file path in the ``TACKLE_CONFIG``
#     environment variable. If set, load the config from this path. This will
#     raise an error if the specified path is not valid.
#
#     If the environment variable is not set, try the default config file path
#     before falling back to the default config values.
#     """
#     if not config:
#         if default_config:
#             logger.debug("Force ignoring user config with default_config switch.")
#             return Settings()
#     if config:
#         logger.debug("Using config from entrypoint.")
#         return Settings(**config)
#
#     # Load the given config file
#     if config_file and config_file is not USER_CONFIG_PATH:
#         logger.debug("Loading custom config from %s.", config_file)
#         if os.path.isfile(config_file):
#             config_file_dict = read_config_file(config_file)
#             return Settings(**config_file_dict)
#         else:
#             raise ConfigDoesNotExistException(
#                 f'Config file {config_file} does not exist.'
#             )
#     try:
#         # Does the user set up a config environment variable?
#         env_config_file = os.environ['TACKLE_CONFIG']
#     except KeyError:
#         # Load an optional user config if it exists
#         # otherwise return the defaults
#         if os.path.exists(USER_CONFIG_PATH):
#             logger.debug("Loading config from %s.", USER_CONFIG_PATH)
#             user_config_file_dict = read_config_file(
#                 expand_path(USER_CONFIG_PATH), 'yaml'
#             )
#             return Settings(**user_config_file_dict)
#         else:
#             logger.debug("User config not found. Loading default config.")
#             return Settings()
#     else:
#         # There is a config environment variable. Try to load it.
#         # Do not check for existence, so invalid file paths raise an error.
#         logger.debug("User config not found or not specified. Loading default config.")
#         env_config_file_dict = read_config_file(env_config_file)
#         return Settings(**env_config_file_dict)
#
