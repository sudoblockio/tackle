"""Example."""
from tackle.models import BaseHook
from pydantic import field_validator


class ThingHook(BaseHook):
    """Do stuff and things."""

    hook_name: str = 'thing'
    stuff: str

    @field_validator('stuff')
    def validate(cls, value):
        # Check if the input is valid - throw error otherwise
        if value == 'not-things':
            raise Exception
        return value

    def exec(self):
        print(self.stuff)
        return self.stuff
