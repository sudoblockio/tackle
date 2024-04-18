import sys
from typing import Any

from InquirerPy import prompt

from tackle import BaseHook, Context, Field, exceptions
from tackle.utils.data_crud import get_readable_key_path


class InquirerPasswordHook(BaseHook):
    """
    Hook for PyInquirer `password` type prompts. Masks the input as the user types it
     in. [Source example](https://github.com/kazhala/InquirerPy/blob/master/examples/password.py)
    """

    hook_name = 'password'

    message: str = Field(
        None,
        description="String message to show when prompting.",
    )
    default: Any = Field(
        None,
        description="Default selection.",
        alias="d",
    )

    args: list = ['message', 'default']

    def exec(self, context: Context) -> str:
        if self.message is None:
            self.message = get_readable_key_path(context.key_path) + ' >>>'

        if not context.no_input:
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
