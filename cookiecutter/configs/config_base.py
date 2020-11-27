"""Main config / settings manager."""
# from collections import OrderedDict
# import os
# import logging
#
# from pydantic import BaseSettings
# from cookiecutter.models import Settings
# from typing import Dict, Any, Union
#
# from cookiecutter.utils.paths import expand_path
# from cookiecutter.utils.reader import read_config_file
#
# logger = logging.getLogger(__name__)
#
# USER_CONFIG_PATH = os.path.expanduser('~/.cookiecutterrc')


# DEFAULT_ABBREVIATIONS: Dict = {
#     'gh': 'https://github.com/{0}.git',
#     'gl': 'https://gitlab.com/{0}.git',
#     'bb': 'https://bitbucket.org/{0}',
# }
#
#
#
# def expand_path(path):
#     """Expand both environment variables and user home in the given path."""
#     path = os.path.expandvars(path)
#     path = os.path.expanduser(path)
#     return path
#
#
# class Settings(BaseSettings):
#     """Base settings for run."""
#
#     cookiecutters_dir: str = '~/.cookiecutters/'
#     replay_dir: str = '~/.cookiecutter_replay/'
#
#     tackle_dir: str = '~/.tackle-box'
#
#     rerun_file_suffix: str = 'rerun.yml'
#
#     abbreviations: Dict = {}
#     default_context: Dict = OrderedDict([])
#
#     config_path: str = None
#
#     extra_providers: list = None
#     extra_provider_dirs: list = None
#
#     dump_output: str = 'yaml'
#
#     class Config:
#         env_prefix = 'TACKLE_'
#         env_file_encoding = 'utf-8'
#
#     def __init__(self, **values: Any):
#         super().__init__(**values)
#         self.abbreviations.update(DEFAULT_ABBREVIATIONS)
#
#         self.cookiecutters_dir = expand_path(self.cookiecutters_dir)
#         self.replay_dir = expand_path(self.replay_dir)
#
#     def init(self):
#         print()
#         pass


# def get_settings(
#     config_file: str = None,
#     env_file: str = None,
#     config: Dict = None,
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
#     Otherwise look up the config file path in the ``COOKIECUTTER_CONFIG``
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
#         return Settings(**config, _env_file=env_file)
#
#     # Load the given config file
#     if config_file and config_file is not USER_CONFIG_PATH:
#         logger.debug("Loading custom config from %s.", config_file)
#         config_file_dict = read_config_file(config_file)
#         return Settings(**config_file_dict, _env_file=env_file)
#
#     try:
#         # Does the user set up a config environment variable?
#         env_config_file = os.environ['COOKIECUTTER_CONFIG']
#     except KeyError:
#         # Load an optional user config if it exists
#         # otherwise return the defaults
#         if os.path.exists(USER_CONFIG_PATH):
#             logger.debug("Loading config from %s.", USER_CONFIG_PATH)
#             user_config_file_dict = read_config_file(
#                 expand_path(USER_CONFIG_PATH), 'yaml'
#             )
#             return Settings(**user_config_file_dict, _env_file=env_file)
#         else:
#             logger.debug("User config not found. Loading default config.")
#             return Settings(_env_file=env_file)
#     else:
#         # There is a config environment variable. Try to load it.
#         # Do not check for existence, so invalid file paths raise an error.
#         logger.debug("User config not found or not specified. Loading default config.")
#         env_config_file_dict = read_config_file(env_config_file)
#         return Settings(**env_config_file_dict, _env_file=env_file)
