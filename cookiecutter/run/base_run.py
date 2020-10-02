from pydantic import BaseModel, SecretStr
from typing import Any, Dict
import os

from cookiecutter.exceptions import InvalidModeException


class Run(BaseModel):
    calling_directory = os.path.abspath(os.getcwd())

    template: str = None
    template_name: str = None
    checkout: str = None
    no_input: bool = False
    context_file: str = None
    context_file_version: float = None
    context_key: str = None


    existing_context: Dict = None
    extra_context: Dict = None

    replay: bool = None
    overwrite_if_exists: bool = False
    output_dir: str = '.'
    config_file: str = None
    password: SecretStr = None
    directory: str = None

    skip_if_file_exists: str = False
    accept_hooks: bool = True

    repo_dir: str = None
    cleanup: bool = None

    # _template: str
    # _output_dir: str

    class Config:
        extra: str = 'allow'

    def __init__(self, **data: Any):
        super().__init__(**data)


        if self.replay and ((self.no_input is not False) or (self.extra_context is not None)):
            err_msg = (
                "You can not use both replay and no_input or extra_context "
                "at the same time."
            )
            raise InvalidModeException(err_msg)

