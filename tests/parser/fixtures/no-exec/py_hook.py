from tackle import BaseHook


class MyHook(BaseHook):
    hook_name = 'MyHook'
    is_true: bool = True
    is_false: bool = False

    is_public: bool = True
