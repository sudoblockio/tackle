from tackle.models import BaseHook


class ThingHook(BaseHook):
    """Do stuff and things."""

    type: str = 'thing'
    stuff: str

    def execute(self):
        print(self.stuff)
        return self.stuff
