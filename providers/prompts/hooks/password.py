import sys

from InquirerPy import prompt

from typing import Any

from tackle import BaseHook, Field, Context
from tackle.utils.dicts import get_readable_key_path
from tackle import exceptions


class InquirerPasswordHook(BaseHook):
    """
    Hook for PyInquirer `password` type prompts. Masks the input as the user types it
     in. [Source example](https://github.com/kazhala/InquirerPy/blob/master/examples/password.py)
    """

    hook_name: str = 'password'

    default: Any = Field(None, description="Default that is not filled in.")
    message: str = Field(None, description="String message to show when prompting.")

    args: list = ['message', 'default']

    def exec(self, context: Context) -> str:
        if self.message is None:
            self.message = get_readable_key_path(context.key_path) + ' >>>'

        if not self.no_input:
            question = {
                'type': self.hook_name,
                'name': 'tmp',
                'message': self.message,
            }

            # Handle keyboard exit
            try:
                response = prompt([question])
            except KeyboardInterrupt:
                print("Exiting...")
                sys.exit(0)
            except EOFError:
                raise exceptions.PromptHookCallException(context=context)
            return response['tmp']

        elif self.default:
            return self.default
        else:
            return ""
