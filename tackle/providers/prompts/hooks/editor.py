from PyInquirer import prompt
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
    name: str = Field('tmp', description="Extra key to embed into. Artifact of API.")
    message: str = Field(None, description="String message to show when prompting.")

    _args: list = ['message', 'default']

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.message is None:
            self.message = get_readable_key_path(self.key_path) + ' >>>'

    def execute(self) -> bool:
        if not self.no_input:
            question = {
                'type': self.hook_type,
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
