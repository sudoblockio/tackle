from typing import Union, Any

from pydantic import Field

from tackle import BaseHook
from tackle.utils.dicts import encode_key_path, nested_get
from tackle.exceptions import HookCallException

# Hack because fallback value should be able to be None so None can't be default
# -> string instead
FALLBACK_VALUE = "None"


class GetKeyHook(BaseHook):
    """
    Hook for getting a key based on a key path which is a list with keys and numbers
     for indexes in a list.
    """

    hook_type: str = 'get'
    # fmt: off
    path: Union[list, str] = Field(
        ...,
        description="A list or string with a separator for the path to the value you "
                    "want to update with strings for keys and ints for indexes in the "
                    "list."
    )
    sep: str = Field('/', description="For string paths, a separator for key path.")
    fallback: Any = Field(
        FALLBACK_VALUE, description="Fallback value if the keys is not found."
    )
    args: list = ['path', 'fallback']
    # fmt: on

    def exec(self):
        """Run the hook."""
        value = None
        for i in ['public', 'private', 'temporary', 'existing']:
            try:
                value = nested_get(
                    element=getattr(self, f'{i}_context'),
                    keys=encode_key_path(self.path, self.sep),
                )
            except KeyError:
                pass

            if value is not None:
                break

        if value is None and self.verbose:
            if self.verbose:
                print(f"Could not find a key in {self.path} in any context.")
            if self.fallback == FALLBACK_VALUE:
                raise HookCallException(
                    f"Could not find a key in {self.path} in any context.", context=self
                )
            if self.verbose:
                print(f"Using fallback={self.fallback}.")
            value = self.fallback

        return value
