"""Mode model."""
from pydantic import BaseModel
from typing import Any, Union
from cookiecutter.exceptions import InvalidModeException


class Mode(BaseModel):
    """Mode in which the project is run."""

    no_input: bool = False
    replay: Union[bool, str] = None
    record: Union[bool, str] = None
    rerun: bool = None
    overwrite_if_exists: bool = False
    skip_if_file_exists: bool = False
    accept_hooks: bool = True
    output_dir: str = '.'

    class Config:
        allow_mutation = False

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.replay and self.no_input:
            err_msg = (
                "You can not use both replay and no_input or extra_context "
                "at the same time."
            )
            raise InvalidModeException(err_msg)
