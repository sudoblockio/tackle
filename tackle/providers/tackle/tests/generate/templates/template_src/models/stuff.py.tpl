from pydantic import BaseModel


class Stuff(BaseModel):
    things: str = None