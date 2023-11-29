from tackle import BaseHook

class MyBaseHook(BaseHook):
    hook_name: str = 'base_hook'
    foo: str = 'bar'
    a_str_required: str
    in_base: str
    an_optional_str: str | None = None
