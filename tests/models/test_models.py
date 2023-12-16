from tackle import BaseHook


def test_models_wrong_type_override_base_hook():
    class MyHook(BaseHook):
        hook_name: int = 1

    my_hook = MyHook()
