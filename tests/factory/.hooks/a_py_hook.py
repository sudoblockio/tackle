from tackle import BaseHook


class Foo(BaseHook):
    hook_name: str = "foo"

    def exec(self):
        return self.hook_name
