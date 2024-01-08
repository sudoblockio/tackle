from tackle import get_hook


def test_model_data_hook():
    Hook = get_hook('model_data')
    output = Hook().exec()

    assert 'BaseHook' in output
    assert 'HookCallInput' in output
    assert 'FieldInput' in output
    assert 'DclHookModelConfig' in output
