from tackle.decorators import hook


def a_func(foo: str) -> str:
    return "bar"


def _b_func(foo: str) -> str:
    return "bar"


hook(a_func, is_public=True)
hook(_b_func, name="b_func", is_public=True)
