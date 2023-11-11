"""Example."""
from tackle.models import BaseHook


class ThingHook(BaseHook):
    """Do stuff and things."""

    hook_name: str = 'thing'
    stuff: str

    def exec(self):
        print(self.stuff)
        return self.stuff
