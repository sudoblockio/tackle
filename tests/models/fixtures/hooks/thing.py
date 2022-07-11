"""Example."""
from tackle.models import BaseHook
from pydantic import validator


class ThingHook(BaseHook):
    """Do stuff and things."""

    hook_type: str = 'thing'
    stuff: str

    @validator('stuff')
    def validate(cls, value):
        # Check if the input is valid - throw error otherwise
        if value == 'not-things':
            raise Exception
        return value

    def exec(self):
        print(self.stuff)
        return self.stuff
