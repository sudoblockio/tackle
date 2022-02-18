import sys
from PyInquirer import prompt

from typing import Any
from tackle.models import BaseHook, Field
from tackle.utils.dicts import get_readable_key_path


class InquirerExpandHook(BaseHook):
    """
    Hook for PyInquirer `expand` type prompt.
     [Source example](https://github.com/CITGuru/PyInquirer/blob/master/examples/expand.py)
    """

    hook_type: str = 'expand'

    default: Any = Field(None, description="Default selection.")
    message: str = Field(None, description="String message to show when prompting.")

    _args: list = ['message', 'default']

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.message is None:
            self.message = get_readable_key_path(self.key_path) + ' >>>'

    def execute(self) -> list:
        if not self.no_input:
            question = {
                'type': self.hook_type,
                'name': 'tmp',
                'message': self.message,
            }
            if self.default:
                question.update({'default': self.default})

            response = prompt([question])

            # Handle keyboard exit
            try:
                return response['tmp']
            except KeyError:
                sys.exit(0)
        elif self.default:
            return self.default
        else:
            # When no_input then return empty list
            return []
