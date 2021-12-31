"""Confirm hook."""
import logging
from PyInquirer import prompt
from typing import Any
from pydantic import Field

from tackle.models import BaseHook
from tackle.utils.dicts import get_readable_key_path

logger = logging.getLogger(__name__)


class InquirerConfirmHook(BaseHook):
    """Hook to confirm with a message and return a boolean."""

    hook_type: str = 'confirm'

    default: Any = Field(True, description="Default choice.")
    message: str = Field(None, description="String message to show when prompting.")
    name: str = Field('tmp', description="Extra key to embed into. Artifact of API.")

    _args: list = ['message']

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.message is None:
            self.message = get_readable_key_path(self.key_path_) + ' >>>'

    def execute(self) -> bool:
        if not self.no_input:
            question = {
                'type': 'confirm',
                'name': self.name,
                'message': self.message,
                'default': self.default,
            }
            response = prompt([question])
            if self.name != 'tmp':
                return response
            else:
                return response['tmp']
        elif self.default:
            return self.default
        else:
            # When no_input then return empty list
            return True
