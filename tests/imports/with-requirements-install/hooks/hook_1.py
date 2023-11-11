from tackle.models import BaseHook

from foo import bar

class Hook1(BaseHook):
    hook_name: str = 'hook_1'

    def exec(self):
        return True
