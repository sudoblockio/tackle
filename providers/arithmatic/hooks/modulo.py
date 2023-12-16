from typing import Optional, Union

from tackle import BaseHook, Field


class ModuloHook(BaseHook):
    """
    Hook for taking the modulo of an integer with optionally checking if it is equal
     to another number, 0 by default.
    """
    hook_name: str = 'modulo'
    # Relates to https://github.com/sudoblockio/tackle/issues/183 where we might want to
    # `render_by_default` src
    input: int = Field(
        ...,
        description="The input integer to take the modulo of.",
        # render_by_default=True,
    )
    divisor: int = Field(
        ...,
        description="The divisor to take the modulo with.",
    )
    equal_to: Optional[int] = Field(
        None,
        description="Optional parameter to assert if the modulo is equal to. Returns a "
                    "bool then.",
    )

    args: list = ['input', 'divisor', 'equal_to']

    def exec(self) -> Union[int, bool]:
        if self.equal_to is not None:
            return self.input % self.divisor == self.equal_to
        return self.input % self.divisor
