from tackle import BaseHook, Field


class RangeHook(BaseHook):
    """
    Create a list of integers within a range, ie ->: range 3 1 -> [3,2,1]. If given one
     arg, then that is considered 'stop'. If given two args, they are 'start' and
     'stop'. If given three args, the last arg is for how much to increment through
     range.
    """

    hook_name = 'range'
    # fmt: off
    start: int = Field(
        0,
        description="Starting number.",
    )
    end: int = Field(
        None,
        description="Ending number.",
    )
    increment: int = Field(
        None,
        description="The increment in the range - when start > end, defaults to -1..",
    )
    # fmt: on

    args: list = ['start', 'end', 'increment']

    def exec(self) -> list:
        if self.increment is None:
            self.increment = 1

        if self.end is None:
            self.end = self.start
            self.start = 0

        if self.end < self.start and self.increment == 1:
            self.increment = -1

        return [i for i in range(self.start, self.end, self.increment)]
