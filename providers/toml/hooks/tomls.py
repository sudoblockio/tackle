try:
    import tomli as toml
except ModuleNotFoundError:
    import tomllib as toml

import os
from typing import Union, MutableMapping

from tackle import BaseHook, Field


class TomlHook(BaseHook):
    """Hook for reading toml. Does not support write which needs another provider"""

    hook_name: str = 'toml'
    path: str = Field(..., description="The file path to put read or write to.")
    # data: Union[dict, list, str] = Field(
    #     None,
    #     description="Map/list or renderable string to a map/list key to write.",
    #     render_by_default=True,
    # )
    args: list = ['path', 'data']

    def exec(self) -> Union[MutableMapping, str]:
        self.path = os.path.abspath(os.path.expanduser(os.path.expandvars(self.path)))
        # Make path if it does not exist
        # if not os.path.exists(os.path.dirname(self.path)) and self.data:
        #     os.makedirs(os.path.dirname(self.path))

        # if self.data:
        #     with open(self.path, 'w') as f:
        #         toml.dump(self.data, f)
        #     return self.path
        #
        # else:
        with open(self.path, 'rb') as f:
            data = toml.load(f)
        return data