"""Example."""
from tackle.models import BaseHook


class ThingHook(BaseHook):
    """Do stuff and things."""

    hook_name = 'stuff'
    thing: str

    def exec(self):
        print(self.thing)
        return self.thing
