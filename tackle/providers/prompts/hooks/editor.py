import sys
from InquirerPy import prompt

from typing import Any

from tackle.models import BaseHook, Field
from tackle.utils.dicts import get_readable_key_path


class InquirerEditorHook(BaseHook):
    """
    Hook for PyInquirer `editor` type prompts. Opens an editor like nano to fill in a
     field. [Source example](https://github.com/CITGuru/PyInquirer/blob/master/examples/editor.py)
    """

    hook_type: str = 'editor'
    default: Any = Field(None, description="Default selection.")
    message: str = Field(None, description="String message to show when prompting.")

    args: list = ['message', 'default']

    def exec(self) -> bool:
        if self.message is None:
            self.message = get_readable_key_path(self.key_path) + ' >>>'

        if not self.no_input:
            question = {
                'type': self.hook_type,
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
