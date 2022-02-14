from tackle.main import tackle


def test_provider_pyinquirer_confirm_hook(change_dir, mocker):
    mocker.patch(
        'tackle.providers.prompts.hooks.confirm.prompt', return_value={"tmp": True}
    )
    o = tackle()
    assert o['this']
