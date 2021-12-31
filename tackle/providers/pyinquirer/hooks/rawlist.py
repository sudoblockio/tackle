"""Raw list hook."""
from PyInquirer import prompt
from pydantic import Field

from typing import Any
from tackle.models import BaseHook
from tackle.utils.dicts import get_readable_key_path


class InquirerRawListHook(BaseHook):
    """
    Hook for PyInquirer 'rawlist' type prompts.

    Example: https://github.com/CITGuru/PyInquirer/blob/master/examples/rawlist.py
    :param message: String message to show when prompting.
    :param choices: A list of strings or list of k/v pairs per above description
    :param name: A key to insert the output value to. If not provided defaults to
        inserting into parent key
    :return: String for the answer
    """

    hook_type: str = 'rawlist'

    default: Any = Field(None, description="Default choice.")
    message: str = Field(None, description="String message to show when prompting.")
    name: str = Field('tmp', description="Extra key to embed into. Artifact of API.")

    _args: list = ['message', 'default']

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.message is None:
            self.message = get_readable_key_path(self.key_path_) + ' >>>'

    def execute(self):
        if not self.no_input:
            question = {
                'type': self.type,
                'name': self.name,
                'message': self.message,
                'choices': self.choices,
            }
            if self.default:
                question.update({'default': self.default})

            response = prompt([question])
            if self.name != 'tmp':
                return response
            else:
                return response['tmp']
        elif self.default:
            return self.default
        else:
            # When no_input then return empty list
            return []
