from tackle.utils.hooks import get_hook


def test_utils_hooks_get_hook_python():
    hook = get_hook("py_hook")
    assert hook.hook_name == "py_hook"


def test_utils_hooks_get_hook_dcl():
    hook = get_hook("my_hook")
    assert hook.hook_name == "my_hook"


def test_utils_hooks_get_hook_native():
    hook = get_hook("literal")
    assert hook.hook_name == "literal"


def test_utils_hooks_get_hook_in_a_dir(cd):
    cd('a-dir')
    # hook = get_hook("my_hook")
    # assert hook.hook_name == "my_hook"
    from tackle import tackle

    output = tackle('a-tackle.yaml')
    assert output