from collections import OrderedDict
import os
import copy
import logging

from pydantic import BaseSettings
from typing import Dict, Any

from cookiecutter.utils.reader import read_config_file

DEFAULT_ABBREVIATIONS: Dict = {
    'gh': 'https://github.com/{0}.git',
    'gl': 'https://gitlab.com/{0}.git',
    'bb': 'https://bitbucket.org/{0}',
}

logger = logging.getLogger(__name__)

# New folder structure
#


class Settings(BaseSettings):
    #
    user_config_path = '~/.cookiecutterrc'
    env_file: str = '.env'

    # Legacy
    cookiecutters_dir: str = '~/.cookiecutters/'
    replay_dir: str = '~/.cookiecutter_replay/'

    abbreviations: Dict = {}
    default_context: Dict = OrderedDict([])

    config: Dict = {}

    # env_config_file = os.environ['COOKIECUTTER_CONFIG']

    class Config:
        env_prefix = 'NUKI_'

    def __init__(self, **values: Any):
        super().__init__(**values)
        self.abbreviations.update(DEFAULT_ABBREVIATIONS)

        self.user_config_path = self._expand_path(self.user_config_path)
        self.cookiecutters_dir = self._expand_path(self.cookiecutters_dir)
        self.replay_dir = self._expand_path(self.replay_dir)

        # if self.config:
        #     config = read_config_file(config_file)

        try:
            self.env_file = os.environ['COOKIECUTTER_ENV_FILE']
        except KeyError:
            if os.path.exists(self.user_config_path):
                logger.debug("Loading config from %s.", self.user_config_path)

    def init(self):
        """
        Initializer for environment files. Creates the following files:
        - ~/.cookiecutterrc
        -
        """

        if os.path.exists(self.user_config_path):
            with open(self.user_config_path, 'r') as f:
                pass

    @staticmethod
    def _expand_path(path):
        """Expand both environment variables and user home in the given path."""
        path = os.path.expandvars(path)
        path = os.path.expanduser(path)
        return path

    # def _validat


def get_settings(
    config_file: str = None,
    env_file: str = None,
    config: Dict = None,
    default_config: bool = False,
) -> Settings:
    """

    :param config_file:
    :param env_file:
    :param config:
    :return:
    """
    if not config:
        config = {}

    return Settings(**config, _env_file=env_file)
