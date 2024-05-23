from tackle import BaseHook
from tackle.decorators import public


class MyBaseHook(BaseHook):
    hook_name = 'base_hook'
    foo: str = 'bar'
    a_str_required: str
    in_base: str
    an_optional_str: str | None = None


class HookWithExec(BaseHook):
    hook_name = 'hook_with_exec'
    foo: str = 'bar'
    a_str_required: str

    @public
    def another_method(self):
        return self.foo + self.a_str_required + "2"

    def exec(self):
        return self.foo + self.a_str_required
