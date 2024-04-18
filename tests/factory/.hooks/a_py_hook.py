from tackle import BaseHook


class Foo(BaseHook):
    hook_name = "foo"

    def exec(self):
        return self.hook_name
