from tackle import BaseHook
from art import art


class ArtHook(BaseHook):
    hook_type: str = 'art'

    def exec(self):
        return art("random")
