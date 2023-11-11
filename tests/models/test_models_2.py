from tackle.models import DclHookInput


def test_dcl_hook_input_extra():
    h = DclHookInput(
        **{'foo': 1, 'extends': 'bar'}
    )

    assert h
