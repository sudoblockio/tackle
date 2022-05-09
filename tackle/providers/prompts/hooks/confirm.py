import sys
from InquirerPy import prompt

from tackle.models import BaseHook, Field
from tackle.utils.dicts import get_readable_key_path


class InquirerConfirmHook(BaseHook):
    """
    Hook to confirm with a message and return a boolean.
     [Source example](https://github.com/CITGuru/PyInquirer/blob/master/examples/confirm.py)
    """

    hook_type: str = 'confirm'

    default: bool = Field(True, description="Default choice.")
    message: str = Field(None, description="String message to show when prompting.")

    args: list = ['message']
    _docs_order = 4

    def exec(self) -> bool:
        if self.message is None:
            self.message = get_readable_key_path(self.key_path) + ' >>>'

        if not self.no_input:
            question = {
                'type': 'confirm',
                'name': 'tmp',
                'message': self.message,
                'default': self.default,
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
            # When no_input then return empty list
            return True
