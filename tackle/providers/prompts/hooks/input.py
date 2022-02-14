from PyInquirer import prompt

from typing import Any
from tackle.models import BaseHook, Field
from tackle.utils.dicts import get_readable_key_path


class InquirerInputHook(BaseHook):
    """
    Hook for PyInquirer 'input' type prompts. Allows the user to input a string input.
     [Source example](https://github.com/CITGuru/PyInquirer/blob/master/examples/input.py)
    """

    hook_type: str = 'input'

    default: Any = Field(None, description="Default choice.")
    message: str = Field(None, description="String message to show when prompting.")
    name: str = Field('tmp', description="Extra key to embed into. Artifact of API.")

    _args: list = ['message']
    _docs_order = 0

    def execute(self) -> str:
        if self.message is None:
            self.message = get_readable_key_path(self.key_path) + ' >>>'

        if not self.no_input:
            question = {
                'type': 'input',
                'name': self.name,
                'message': self.message,
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
