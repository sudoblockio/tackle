import os
from typing import Union

try:
    import tomllib as toml
except ImportError:
    import tomli as toml

from tackle import BaseHook, Field


class TomlHook(BaseHook):
    """
    Hook for reading TOML. Wraps python's native toml library which does not support
     writing toml, only reading.
    """

    hook_name = 'toml'
    path: str = Field(..., description="The file path to read or write to.")

    args: list = ['path']

    def exec(self) -> Union[dict, str]:
        self.path = os.path.abspath(os.path.expanduser(os.path.expandvars(self.path)))
        with open(self.path, 'rb') as f:
            data = toml.load(f)
        return data


class TomlDecodeHook(BaseHook):
    """Hook for decoding a TOML string to a dict."""

    hook_name = 'toml_decode'
    data: str = Field(..., description="TOML string to convert to dict.")
    args: list = ['data']

    def exec(self) -> dict:
        return toml.loads(self.data)
