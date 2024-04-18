from tackle import BaseHook


class PyHook(BaseHook):
    hook_name = 'py_hook'
    foo: str = 'bar'
    skip_output: bool = True

    def exec(self):
        pass
