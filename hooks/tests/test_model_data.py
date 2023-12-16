from tackle import tackle, get_hook


def test_model_data_get(base_hooks_dir):
    output = tackle(raw_input={'data->': 'model_data'})

    assert 'BaseHook' in output['data']


def test_model_data_hook():
    Hook = get_hook('model_data')
    output = Hook().exec()

    assert output
