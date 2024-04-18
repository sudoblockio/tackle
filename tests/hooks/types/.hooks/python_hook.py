from tackle import BaseHook


class PyHook(BaseHook):
    hook_name = 'py_hook'
    foo: str
