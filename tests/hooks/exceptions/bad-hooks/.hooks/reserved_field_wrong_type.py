from tackle import BaseHook


class Hook1(BaseHook):
    hook_name = 'hook_1'

    is_public: bool = True

    # args should be list or str - not dict
    args: dict = {'foo': 'bar'}

    def exec(self):
        return True
