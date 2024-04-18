from tackle import BaseHook


class MyHook(BaseHook):
    hook_name = 'MyHook'
    is_true: bool = True
    is_false: bool = False

    def exec(self):
        return self.model_dump(exclude=set(BaseHook.model_fields.keys()))
