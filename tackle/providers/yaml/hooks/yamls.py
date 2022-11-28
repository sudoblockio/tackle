from ruamel.yaml import YAML
import os
from typing import Union

from tackle.models import BaseHook, Field


class YamlHook(BaseHook):
    """
    Hook for reading and writing yaml. Hook reads from `path` if no `data` field is
     provided, otherwise it writes the `data` to `path`.
    """

    hook_type: str = 'yaml'
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

        yaml = YAML()
        if self.data:
            with open(self.path, 'w') as f:
                yaml.dump(self.data, f)
            return self.path

        else:
            with open(self.path, 'r') as f:
                data = yaml.load(f)

            # TODO: Improve this - https://github.com/robcxyz/tackle/issues/56
            import json

            data = json.loads(json.dumps(data))

            return data


class YamlEncodeHook(BaseHook):
    """Hook for converting a dict to a yaml encoded string."""

    hook_type: str = 'yamlencode'
    data: Union[dict, list, str] = Field(
        ...,
        description="Map/list or renderable string to data to convert to yaml string.",
        render_by_default=True,
    )
    args: list = ['data']

    def exec(self) -> Union[dict, str]:
        from io import StringIO

        yaml = YAML()
        options = {}
        string_stream = StringIO()
        yaml.dump(self.data, string_stream, **options)
        output_str = string_stream.getvalue()
        string_stream.close()
        return output_str


class YamlDecodeHook(BaseHook):
    """Hook for decoding a yaml string to a dict."""

    hook_type: str = 'yamldecode'
    data: str = Field(..., description="Yaml string to convert to dict.")
    args: list = ['data']

    def exec(self) -> dict:
        yaml = YAML(typ='safe', pure=True)
        output = yaml.load(self.data)
        return output
