import sys

from InquirerPy import prompt

from typing import Any

from tackle.models import BaseHook, Field
from tackle.utils.dicts import get_readable_key_path


class InquirerPasswordHook(BaseHook):
    """
    Hook for PyInquirer `password` type prompts. Masks the input as the user types it
     in. [Source example](https://github.com/CITGuru/PyInquirer/blob/master/examples/password.py)
    """

    hook_type: str = 'password'

    default: Any = Field(None, description="Default choice.")
    message: str = Field(None, description="String message to show when prompting.")

    args: list = ['message', 'default']

    def exec(self) -> str:
        if self.message is None:
            self.message = get_readable_key_path(self.key_path) + ' >>>'

        if not self.no_input:
            question = {
                'type': self.hook_type,
                'name': 'tmp',
                'message': self.message,
                # 'default': self.default,
            }

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
            return ""
