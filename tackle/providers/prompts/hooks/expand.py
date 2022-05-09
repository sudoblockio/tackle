import sys
from InquirerPy import prompt

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

    args: list = ['message', 'default']

    def exec(self) -> list:
        if self.message is None:
            self.message = get_readable_key_path(self.key_path) + ' >>>'

        if not self.no_input:
            question = {
                'type': self.hook_type,
                'name': 'tmp',
                'message': self.message,
            }
            if self.default:
                question.update({'default': self.default})

            # Handle keyboard exit
            try:
                response = prompt([question])
            except KeyboardInterrupt:
                print("Exiting...")
                sys.exit(0)
            return response['tmp']

        elif self.default:
            return self.default
        else:
            # When no_input then return empty list
            return []
