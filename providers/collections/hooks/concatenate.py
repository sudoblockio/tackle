import itertools

from tackle import BaseHook, Field


class ConcatenateHook(BaseHook):
    """Hook for concatenating a list of items."""

    hook_name = 'concat'
    # Relates to https://github.com/sudoblockio/tackle/issues/183 where we might want to
    # `render_by_default` src
    src: list = Field(
        ...,
        description="A list to concatenate the items of.",
        # render_by_default=True,
    )

    args: list = ['src']

    def exec(self) -> list:
        return list(itertools.chain.from_iterable(self.src))
