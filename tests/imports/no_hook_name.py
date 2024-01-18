from tackle import BaseHook


class MyHook(BaseHook):
    hook_name: list = ['bar']

    def exec(self):
        return self.foo
