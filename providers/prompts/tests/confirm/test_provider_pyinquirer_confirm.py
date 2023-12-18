from providers.prompts.hooks.confirm import InquirerConfirmHook
from tackle import Context


def test_provider_pyinquirer_confirm_hook(mocker):
    mocker.patch('providers.prompts.hooks.confirm.prompt', return_value={"tmp": True})
    context = Context(key_path=[])
    hook = InquirerConfirmHook()
    output = hook.exec(context=context)

    assert output
