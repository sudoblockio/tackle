import os
import configparser
from typing import Union

from tackle.models import BaseHook, Field


class IniHook(BaseHook):
    """
    Hook for reading and writing ini files. Hook reads from `path` if no `data` field is
     provided, otherwise it writes the `data` to `path`.
    """

    hook_type: str = 'ini'
    path: str = Field(..., description="The file path to put read or write to.")
    data: Union[dict, list, str] = Field(
        None,
        description="Map or renderable string to a map key to write. Must have three "
        "levels for the section, key, and value - ie "
        "{section:{key1:value1, key2:value2}}.",
        render_by_default=True,
    )
    _args = ['path', 'data']

    def execute(self) -> Union[dict, str, list]:
        self.path = os.path.abspath(os.path.expanduser(os.path.expandvars(self.path)))
        # Make path if it does not exist
        if not os.path.exists(os.path.dirname(self.path)) and self.data:
            os.makedirs(os.path.dirname(self.path))

        config = configparser.ConfigParser()

        if self.data:
            for section, items in self.data.items():
                config.add_section(section)
                for k, v in items.items():
                    config.set(section, k, v)
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
