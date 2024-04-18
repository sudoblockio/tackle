from tackle import BaseHook, Context, Field, exceptions


class SumHook(BaseHook):
    """Hook for summing a list of numbers."""

    hook_name = 'sum'
    input: list[int | float | dict] = Field(
        ...,
        description="The list to sum.",
    )
    attribute: str | None = Field(
        None,
        description="If the input is a list of objects, an attribute within the object "
        "to sum over.",
    )

    args: list = ['input']

    def exec(self, context: Context) -> int | float:
        if isinstance(self.input[0], dict):
            if self.attribute is None:
                raise exceptions.HookCallException(
                    "Need to supply an `attribute` field if summing over " "an object.",
                    context=context,
                )
            return sum([i[self.attribute] for i in self.input])
        return sum(self.input)


class AverageHook(BaseHook):
    """Hook for taking the average of a list of numbers."""

    hook_name = 'average'
    input: list[int | float | dict] = Field(
        ...,
        description="The list to calculate the average from.",
    )
    attribute: str | None = Field(
        None,
        description="If the input is a list of objects, an attribute within the object "
        "to calculate the average over.",
    )

    args: list = ['input']

    def exec(self, context: Context) -> int | float:
        if not self.input:
            raise exceptions.HookCallException(
                "The input list is empty.",
                context=context,
            )

        if isinstance(self.input[0], dict):
            if self.attribute is None:
                raise exceptions.HookCallException(
                    "Need to supply an `attribute` field if calculating the average over "
                    "an object.",
                    context=context,
                )
            total = sum(i[self.attribute] for i in self.input if self.attribute in i)
            count = sum(1 for i in self.input if self.attribute in i)
        else:
            total = sum(self.input)
            count = len(self.input)

        if count == 0:
            raise exceptions.HookCallException(
                "No valid elements to calculate the average.",
                context=context,
            )

        return total / count


class ModuloHook(BaseHook):
    """
    Hook for taking the modulo of an integer with optionally checking if it is equal
     to another number, 0 by default.
    """

    hook_name = 'modulo'
    # Relates to https://github.com/sudoblockio/tackle/issues/183 where we might want to
    # `render_by_default` src
    input: int = Field(
        ...,
        description="The input integer to take the modulo of.",
    )
    divisor: int = Field(
        ...,
        description="The divisor to take the modulo with.",
    )
    equal_to: int | None = Field(
        None,
        description="Optional parameter to assert if the modulo is equal to. Returns a "
        "bool then.",
    )

    args: list = ['input', 'divisor', 'equal_to']

    def exec(self) -> int | bool:
        if self.equal_to is not None:
            return self.input % self.divisor == self.equal_to
        return self.input % self.divisor
