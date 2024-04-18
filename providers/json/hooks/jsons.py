import json
import os
from typing import Union

from tackle import BaseHook, Field


class JsonHook(BaseHook):
    """
    Hook for reading and writing json. Hook reads from `path` if no `data` field is
     provided, otherwise it writes the `data` to `path`.
    """

    hook_name = 'json'
    path: str = Field(..., description="The file path to put read or write to.")
    data: Union[dict, list, str] = Field(
        None,
        description="Map/list or renderable string to a map/list key to write.",
        render_by_default=True,
    )
    args: list = ['path', 'data']

    def exec(self) -> Union[dict, str]:
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


class JsonEncodeHook(BaseHook):
    """Hook for converting a dict to a JSON encoded string."""

    hook_name = 'json_encode'
    data: Union[dict, list, str] = Field(
        ...,
        description="Map/list or renderable string to data to convert to JSON string.",
        render_by_default=True,
    )
    args: list = ['data']

    def exec(self) -> str:
        return json.dumps(self.data)


class JsonDecodeHook(BaseHook):
    """Hook for decoding a JSON string to a dict."""

    hook_name = 'json_decode'
    data: str = Field(..., description="JSON string to convert to dict.")
    args: list = ['data']

    def exec(self) -> Union[dict, list]:
        return json.loads(self.data)
