"""Example."""
from tackle.models import BaseHook


class StuffHook(BaseHook):
    """Do stuff and things."""

    hook_type: str = 'stuff'
    thing: str

    def exec(self):
        print(self.thing)
        return self.thing
