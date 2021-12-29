"""Random number / string hooks."""
import random
import string
import logging

from tackle.models import BaseHook, Field
from pydantic import validator
from tackle.exceptions import HookCallException

logger = logging.getLogger(__name__)


class RandomHexHook(BaseHook):
    """Hook  for `random_hex`. Lists the contents of a directory."""

    hook_type: str = 'random_hex'
    length: int = Field(8, description="Number for number of digits - default 8")

    _args: list = ['length']

    def execute(self) -> str:
        return ''.join(['%0', str(self.length), 'x']) % random.randrange(
            16 ** self.length
        )


class RandomStringHook(BaseHook):
    """Hook  for `random_string`. Lists the contents of a directory."""

    hook_type: str = 'random_string'
    string_case: str = Field(
        'lower', description="Case of output, one of `upper` or `lower`"
    )
    length: int = Field(8, description="Length of the random string.")

    _args: list = ['length', 'string_case']

    @validator('string_case', allow_reuse=True)
    def validate_string_case2(cls, v):
        if v not in ['upper', 'lower']:
            raise HookCallException(
                "Field `string_case` must be one of 'upper' or 'lower'."
            )
        return v

    def execute(self):
        if self.string_case == 'upper':
            return ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=self.length)
            )
        elif self.string_case == 'lower':
            return ''.join(
                random.choices(string.ascii_lowercase + string.digits, k=self.length)
            )
