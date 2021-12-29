"""JSON hooks."""
import logging
import json
from typing import Union

from tackle.models import BaseHook, Field

logger = logging.getLogger(__name__)


class JsonHook(BaseHook):
    """
    Hook for json. If no `contents` is provided, the hook reads from path. Otherwise
     it writes the `contents`. When writing, returns path. When reading, returns dict.
    """

    hook_type: str = 'json'
    path: str = Field(..., description="The path to write the file.")
    contents: dict = Field(None, description="A dict to write")

    _args: list = ['path', 'contents']

    def execute(self) -> Union[dict, str]:
        if self.contents:
            with open(self.path, 'w') as f:
                json.dump(self.contents, f)
            return self.path

        else:
            with open(self.path, 'r') as f:
                contents = json.load(f)
            return contents
