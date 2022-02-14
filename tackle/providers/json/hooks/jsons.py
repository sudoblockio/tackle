import json
import os
from typing import Union

from tackle.models import BaseHook, Field


class JsonHook(BaseHook):
    """
    Hook for reading and writing json. Hook reads from `path` if no `data` field is
     provided, otherwise it writes the `data` to `path`.
    """

    hook_type: str = 'json'
    path: str = Field(..., description="The file path to put read or write to.")
    data: Union[dict, list, str] = Field(
        None,
        description="Map/list or renderable string to a map/list key to write.",
        render_by_default=True,
    )
    _args = ['path', 'data']

    def execute(self) -> Union[dict, str]:
        self.path = os.path.abspath(os.path.expanduser(os.path.expandvars(self.path)))
        # Make path if it does not exist
        if not os.path.exists(os.path.dirname(self.path)) and self.data:
            os.makedirs(os.path.dirname(self.path))

        if self.data:
            with open(self.path, 'w') as f:
                json.dump(self.data, f)
            return self.path
        else:
            with open(self.path, 'r') as f:
                data = json.load(f)
            return data
