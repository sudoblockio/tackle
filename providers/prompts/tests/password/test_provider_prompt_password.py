import pytest

from providers.prompts.hooks.password import InquirerPasswordHook


@pytest.fixture()
def run_mocked_hook(mocker, context):
    def f(return_value, **kwargs):
        # Patch the `prompt` method which is called by the hook and will since it
        # requires user input from terminal
        mocker.patch(
            'providers.prompts.hooks.password.prompt', return_value=return_value
        )
        hook = InquirerPasswordHook(**kwargs)
        output = hook.exec(context=context)

        return output

    return f


def test_provider_prompt_password_basic(run_mocked_hook):
    output = run_mocked_hook(
        return_value={"tmp": "things"},
    )

    assert output == 'things'
