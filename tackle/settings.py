"""Settings initializer."""
from pydantic import BaseSettings, Field
from typing import Dict
import os
import logging
import pathlib
from xdg import xdg_config_home  # When adding replay functionality -> xdg_state_home

from tackle.utils.files import read_config_file

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Base settings that are immutable during main runtime."""

    tackle_dir: str = os.path.join(xdg_config_home(), 'tackle')
    config_path: str = os.path.join(tackle_dir, 'settings.yaml')
    provider_dir: str = os.path.join(tackle_dir, 'providers')

    extra_providers: list = Field(
        None, description="Extra providers to import into each context."
    )
    default_tackle_file: str = Field(
        None, description="If set, this will be the file if no argument is provided."
    )

    class Config:
        env_prefix = 'TACKLE_'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = "ignore"

    def __init__(self, **values: Dict):
        super().__init__(**values)
        if not os.path.isdir(self.provider_dir):
            pathlib.Path(self.provider_dir).mkdir(parents=True, exist_ok=True)

        if os.path.exists(self.config_path):
            global_settings = read_config_file(self.config_path)
            for k, v in global_settings:
                setattr(self, k, v)


settings = Settings()
