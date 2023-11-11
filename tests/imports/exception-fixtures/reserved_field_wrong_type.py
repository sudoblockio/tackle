from tackle import BaseHook


class Hook1(BaseHook):
    hook_name: str = 'hook_1'

    # is_public: str = 'wrong'
    # args should be list or str - not dict
    args: dict = {}

    def exec(self):
        return True
