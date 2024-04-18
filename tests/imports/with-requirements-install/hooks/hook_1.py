from foo import bar  # noqa

from tackle.models import BaseHook


class Hook1(BaseHook):
    hook_name = 'hook_1'

    def exec(self):
        return True
