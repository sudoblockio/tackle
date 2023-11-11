from tackle import BaseHook
from art import art


class ArtHook(BaseHook):
    hook_name: str = 'art'

    def exec(self):
        return art("random")
