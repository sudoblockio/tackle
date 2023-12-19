from providers.prompts.hooks.confirm import InquirerConfirmHook


def test_provider_pyinquirer_confirm_hook(mocker, context):
    mocker.patch('providers.prompts.hooks.confirm.prompt', return_value={"tmp": True})
    hook = InquirerConfirmHook()
    output = hook.exec(context=context)

    assert output
