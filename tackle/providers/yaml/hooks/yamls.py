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

            # TODO: Improve this - https://github.com/robcxyz/tackle-box/issues/56
            import json

            data = json.loads(json.dumps(data))

            return data
