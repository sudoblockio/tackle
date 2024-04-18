import configparser
import os
from io import StringIO
from typing import Union

from tackle import BaseHook, Field


class IniHook(BaseHook):
    """
    Hook for reading and writing ini files. Hook reads from `path` if no `data` field is
     provided, otherwise it writes the `data` to `path`.
    """

    hook_name = 'ini'
    path: str = Field(..., description="The file path to put read or write to.")
    data: Union[dict, list, str] = Field(
        None,
        description="Map or renderable string to a map key to write. Must have three "
        "levels for the section, key, and value - ie "
        "{section:{key1:value1, key2:value2}}.",
        render_by_default=True,
    )
    allow_no_value: bool = Field(True, description="Whether to allow a no values.")
    args: list = ['path', 'data']

    def exec(self) -> Union[dict, str, list]:
        self.path = os.path.abspath(os.path.expanduser(os.path.expandvars(self.path)))
        # Make path if it does not exist
        if not os.path.exists(os.path.dirname(self.path)) and self.data:
            os.makedirs(os.path.dirname(self.path))

        config = configparser.ConfigParser(allow_no_value=self.allow_no_value)

        if self.data:
            for section, items in self.data.items():
                config.add_section(section)
                for k, v in items.items():
                    if v is None and self.allow_no_value:
                        config.set(section, k)
                    else:
                        config.set(section, k, str(v))
            with open(self.path, 'w') as f:
                config.write(f)

            return self.path

        else:
            output = {}
            config.read(self.path)
            for section in config.sections():
                output[section] = {}
                for option in config.options(section):
                    output[section][option] = config.get(section, option)

            return output


class IniEncodeHook(BaseHook):
    """Hook for converting a dict to an ini encoded string."""

    hook_name = 'ini_encode'
    data: dict | str = Field(
        ...,
        description="Map or renderable string to data to convert to ini string.",
        render_by_default=True,
    )
    args: list = ['data']

    def exec(self) -> str:
        if not isinstance(self.data, dict):
            raise ValueError("INI serialization requires a dictionary input")

        config = configparser.ConfigParser()
        # https://stackoverflow.com/a/19359720/12642712
        config.optionxform = str

        for section, values in self.data.items():
            config[section] = values

        with StringIO() as string_stream:
            config.write(string_stream)
            return string_stream.getvalue()


class IniDecodeHook(BaseHook):
    """Hook for decoding an ini string to a dict."""

    hook_name = 'ini_decode'
    data: str = Field(
        ...,
        description="Yaml string to convert to dict.",
    )
    args: list = ['data']

    def exec(self) -> dict:
        config = configparser.ConfigParser()
        # https://stackoverflow.com/a/19359720/12642712
        config.optionxform = str
        string_stream = StringIO(self.data)
        config.read_file(string_stream)

        # Convert to a regular dictionary
        output = {section: dict(config.items(section)) for section in config.sections()}
        return output
