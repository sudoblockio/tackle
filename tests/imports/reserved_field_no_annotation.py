from tackle import BaseHook


class Hook1(BaseHook):
    hook_name = 'hook_1'

    # Should be is_public: bool = True
    is_public = True

    def exec(self):
        return True
