"""Things"""
from pydantic import BaseModel


class Stuff(BaseModel):
    """All of it."""

    things: str = None
