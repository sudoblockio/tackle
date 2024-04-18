from tackle import BaseHook


class MyHook(BaseHook):
    hook_name = 'my_hook'
    foo: str = 'bar'
    skip_output: bool = True

    def exec(self):
        pass
