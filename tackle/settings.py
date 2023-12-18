import logging
import os
import pathlib

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from ruyaml import YAML
from xdg import xdg_config_home  # When adding replay functionality -> xdg_state_home

from tackle.utils.files import read_config_file

logger = logging.getLogger(__name__)

xdg_config_home = xdg_config_home()


class Settings(BaseSettings):
    """Base settings that are immutable during main runtime."""

    tackle_dir: str = Field(
        os.path.join(xdg_config_home, 'tackle'),
        description="Directory where tackle config is",
    )
    config_path: str = Field(
        os.path.join(xdg_config_home, 'tackle', 'config.yaml'),
        description="File path to where tackle config is",
    )
    providers_dir: str = Field(
        os.path.join(xdg_config_home, 'tackle', 'providers'),
        description="Directory where tackle providers are",
    )
    prompt_for_installs: bool = Field(
        True,
        description="Prompt when a provider wants to install a requirement.",
    )

    # TODO: WIP - Using cache for native providers
    local_install: bool = Field(
        True,
        description="Boolean to create entrypoint as `tkl` and recompile all the"
        " providers one each run.",
    )
    # # TODO: RM or use
    # extra_providers: Optional[list] = Field(
    #     [],
    #     description="Extra providers to import into each context.",
    # )
    # # TODO: RM or use
    # default_tackle_file: Optional[str] = Field(
    #     None,
    #     description="If set, this will be the file if no argument is provided.",
    # )

    model_config = SettingsConfigDict(
        env_prefix='TACKLE_',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
    )


def update_settings(settings: Settings):  # noqa
    if not os.path.isdir(settings.providers_dir):
        pathlib.Path(settings.providers_dir).mkdir(parents=True, exist_ok=True)

    if not os.path.isfile(settings.config_path):
        # Create a config.yaml file if it doesn't exist
        yaml = YAML()
        with open(settings.config_path, 'w') as f:
            yaml.default_flow_style = False
            yaml.dump(settings.model_dump(exclude={'config_path'}), f)

    if os.path.exists(settings.config_path):
        global_settings = read_config_file(settings.config_path)
        if global_settings is None or not isinstance(global_settings, dict):
            return
        for k, v in global_settings.items():
            try:
                setattr(settings, k, v)
            except ValidationError as e:
                logger.info(f"Error setting config key={k} with value={v}\n{e}.")


settings = Settings()
update_settings(settings=settings)

pass
