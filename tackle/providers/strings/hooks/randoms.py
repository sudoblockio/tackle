import random
import string
from pydantic import validator

from tackle.models import BaseHook, Field
from tackle.exceptions import HookCallException


class RandomStringHook(BaseHook):
    """Hook for `random_string`. Lists the contents of a directory."""

    # TODO: Update this interface?  Rm string_case replace with --lower/upper flag?

    hook_type: str = 'random_string'
    length: int = Field(8, description="Length of the random string.")
    case: str = Field('lower', description="Case of output, one of `upper` or `lower`")
    upper: bool = Field(False, description="Flag for upper case. Overrides `case`.")

    args: list = ['length', 'case']
    _docs_order = 6

    @validator('case')
    def validate_string_case(cls, v):
        if v not in ['upper', 'lower']:
            raise HookCallException(
                "Field `string_case` must be one of 'upper' or 'lower'."
            )
        return v

    def exec(self) -> str:
        if self.upper:
            self.case = 'upper'

        if self.case == 'upper':
            return ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=self.length)
            )
        elif self.case == 'lower':
            return ''.join(
                random.choices(string.ascii_lowercase + string.digits, k=self.length)
            )


class RandomHexHook(BaseHook):
    """Hook  for `random_hex`. Lists the contents of a directory."""

    hook_type: str = 'random_hex'
    length: int = Field(8, description="Number for number of digits - default 8")

    args: list = ['length']
    _docs_order = 7

    def exec(self) -> str:
        return ''.join(['%0', str(self.length), 'x']) % random.randrange(
            16 ** self.length
        )
