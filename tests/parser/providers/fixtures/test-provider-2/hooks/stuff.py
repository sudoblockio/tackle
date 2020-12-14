from tackle.models import BaseHook


class ThingHook(BaseHook):
    """Do stuff and things."""

    type: str = 'stuff'
    thing: str

    def execute(self):
        print(self.thing)
        return self.thing
