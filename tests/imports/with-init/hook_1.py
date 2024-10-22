from tackle.models import BaseHook

from hook_2 import Hook2

class Hook1(BaseHook):
    hook_name = 'hook_1'

    hook_2: Hook2 = None
    __is_public__ = True

    def exec(self):
        return True
