from tackle import BaseHook


class MyHook(BaseHook):
    hook_name: str = 'no_exec'
    foo: str = 'bar'
