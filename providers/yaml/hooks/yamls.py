import os
from io import StringIO
from typing import Union

from ruyaml import YAML
from ruyaml.composer import ComposerError

from tackle import BaseHook, Field


def str_representer(dumper, data):
    """Add support for multiline strings when dumping otherwise mangled."""
    # Credit: https://gist.github.com/alertedsnake/c521bc485b3805aa3839aef29e39f376
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


class YamlHook(BaseHook):
    """
    Hook for reading and writing yaml. Hook reads from `path` if no `data` field is
     provided, otherwise it writes the `data` to `path`.
    """

    hook_name = 'yaml'
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

        yaml.default_flow_style = False
        yaml.indent(sequence=4, offset=2)
        yaml.representer.add_representer(str, str_representer)

        if self.data:
            with open(self.path, 'w') as f:
                yaml.dump(self.data, f)
            return self.path

        else:
            try:
                with open(self.path, 'r') as f:
                    data = yaml.load(f)
            except ComposerError:
                data = []
                with open(self.path, 'r') as f:
                    for doc in yaml.load_all(f):
                        data.append(doc)

            # TODO: Improve this - https://github.com/sudoblockio/tackle/issues/56
            import json

            data = json.loads(json.dumps(data))

            return data


class YamlEncodeHook(BaseHook):
    """Hook for converting a dict to a yaml encoded string."""

    hook_name = 'yaml_encode'
    data: Union[dict, list, str] = Field(
        ...,
        description="Map/list or renderable string to data to convert to yaml string.",
        render_by_default=True,
    )
    args: list = ['data']

    def exec(self) -> str:
        yaml = YAML()
        with StringIO() as string_stream:
            yaml.dump(self.data, string_stream)
            return string_stream.getvalue()


class YamlDecodeHook(BaseHook):
    """Hook for decoding a yaml string to a dict."""

    hook_name = 'yaml_decode'
    data: str = Field(..., description="Yaml string to convert to dict.")
    args: list = ['data']

    def exec(self) -> dict:
        yaml = YAML(typ='safe', pure=True)
        output = yaml.load(self.data)
        return output
