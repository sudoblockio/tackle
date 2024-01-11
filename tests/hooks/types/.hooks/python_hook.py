from tackle import BaseHook


class PyHook(BaseHook):
    hook_name: str = 'py_hook'
    foo: str
