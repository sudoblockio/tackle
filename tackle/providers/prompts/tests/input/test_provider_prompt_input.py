from tackle.main import tackle


def test_provider_pyinquirer_input_hook(change_dir, mocker):
    mocker.patch(
        'tackle.providers.prompts.hooks.input.prompt', return_value={"tmp": True}
    )
    o = tackle()
    assert o['this']
