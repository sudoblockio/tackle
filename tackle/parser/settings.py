"""Settings initializer."""
import os
import logging

from tackle.models import Settings

from tackle.utils.paths import expand_path
from tackle.utils.reader import read_config_file
from tackle.exceptions import ConfigDoesNotExistException

logger = logging.getLogger(__name__)

USER_CONFIG_PATH = os.path.expanduser('~/.tacklerc')


def get_settings(
    config_file: str = None,
    env_file: str = None,
    config: dict = None,
    default_config: bool = False,
) -> 'Settings':
    """
    Return the user config as a dict.

    If ``default_config`` is True, ignore ``config_file`` and return default
    values for the config parameters.

    If a path to a ``config_file`` is given, that is different from the default
    location, load the user config from that.

    Otherwise look up the config file path in the ``TACKLE_CONFIG``
    environment variable. If set, load the config from this path. This will
    raise an error if the specified path is not valid.

    If the environment variable is not set, try the default config file path
    before falling back to the default config values.
    """
    if not config:
        if default_config:
            logger.debug("Force ignoring user config with default_config switch.")
            return Settings()
    if config:
        logger.debug("Using config from entrypoint.")
        return Settings(**config, _env_file=env_file)

    # Load the given config file
    if config_file and config_file is not USER_CONFIG_PATH:
        logger.debug("Loading custom config from %s.", config_file)
        if os.path.isfile(config_file):
            config_file_dict = read_config_file(config_file)
            return Settings(**config_file_dict, _env_file=env_file)
        else:
            raise ConfigDoesNotExistException(
                f'Config file {config_file} does not exist.'
            )
    try:
        # Does the user set up a config environment variable?
        env_config_file = os.environ['TACKLE_CONFIG']
    except KeyError:
        # Load an optional user config if it exists
        # otherwise return the defaults
        if os.path.exists(USER_CONFIG_PATH):
            logger.debug("Loading config from %s.", USER_CONFIG_PATH)
            user_config_file_dict = read_config_file(
                expand_path(USER_CONFIG_PATH), 'yaml'
            )
            return Settings(**user_config_file_dict, _env_file=env_file)
        else:
            logger.debug("User config not found. Loading default config.")
            return Settings(_env_file=env_file)
    else:
        # There is a config environment variable. Try to load it.
        # Do not check for existence, so invalid file paths raise an error.
        logger.debug("User config not found or not specified. Loading default config.")
        env_config_file_dict = read_config_file(env_config_file)
        return Settings(**env_config_file_dict, _env_file=env_file)
