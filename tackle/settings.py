"""Global settings initialized from config file or environment variables ."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import logging
import pathlib
from typing import Optional
from xdg import xdg_config_home  # When adding replay functionality -> xdg_state_home

from tackle.utils.files import read_config_file

logger = logging.getLogger(__name__)

xdg_home = xdg_config_home()


class Settings(BaseSettings):
    """Base settings that are immutable during main runtime."""

    tackle_dir: str = Field(
        os.path.join(xdg_home, 'tackle'),
        description="",
    )
    config_path: str = Field(
        os.path.join(xdg_home, 'tackle', 'config.yaml'),
        description="",
    )
    provider_dir: str = Field(
        os.path.join(xdg_home, 'tackle', 'providers'),
        description="",
    )
    local_install: bool = Field(
        True,
        description="Boolean to create entrypoint as `tkl` and recompile all the"
                    " providers one each run."
    )
    prompt_for_installs: bool = Field(
        False,
        description="",
    )

    # TODO: RM or use
    extra_providers: Optional[list] = Field(
        None,
        description="Extra providers to import into each context.",
    )
    # TODO: RM or use
    default_tackle_file: Optional[str] = Field(
        None,
        description="If set, this will be the file if no argument is provided.",
    )

    model_config = SettingsConfigDict(
        env_prefix='TACKLE_',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra="ignore",
    )


def update_settings(settings: Settings):
    if not os.path.isdir(settings.provider_dir):
        pathlib.Path(settings.provider_dir).mkdir(parents=True, exist_ok=True)

    if os.path.exists(settings.config_path):
        global_settings = read_config_file(settings.config_path)
        for k, v in global_settings:
            setattr(settings, k, v)


settings = Settings()
update_settings(settings=settings)
