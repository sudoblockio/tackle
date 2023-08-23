import itertools

from tackle import BaseHook, Field


class ConcatenateHook(BaseHook):
    """Hook for concatenating a list of items."""

    hook_type: str = 'concat'
    # fmt: off
    src: list = Field(
        ..., description="A list to concatenate the items of.", render_by_default=True)
    # fmt: on

    args: list = ['src']

    def exec(self) -> list:
        return list(itertools.chain.from_iterable(self.src))
