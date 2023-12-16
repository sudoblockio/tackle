from tackle import BaseHook


class MyHook(BaseHook):
    foo: str = 'bar'

    def exec(self):
        return self.foo
