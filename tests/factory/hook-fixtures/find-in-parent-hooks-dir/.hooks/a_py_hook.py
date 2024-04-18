from tackle import BaseHook


class Stuff(BaseHook):
    hook_name = "stuff"

    def exec(self):
        return self.hook_name
