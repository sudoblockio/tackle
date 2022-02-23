from tackle.main import tackle


def test_provider_prompts_password_hook(change_dir, mocker):
    mocker.patch(
        'tackle.providers.prompts.hooks.password.prompt', return_value={"tmp": True}
    )
    o = tackle()
    assert o['this']
