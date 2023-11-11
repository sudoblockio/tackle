from tackle.models import BaseHook


class Hook1(BaseHook):
    hook_name: str = 'hook_1'

    def exec(self):
        return True
