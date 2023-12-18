import pytest

from providers.prompts.hooks.input import InquirerInputHook
from tackle import Context


@pytest.fixture()
def run_mocked_hook(mocker):
    def f(return_value, **kwargs):
        # Patch the `prompt` method which is called by the hook and will since it
        # requires user input from terminal
        mocker.patch('providers.prompts.hooks.input.prompt', return_value=return_value)
        context = Context(key_path=[])
        hook = InquirerInputHook(**kwargs)
        output = hook.exec(context=context)

        return output

    return f


def test_provider_prompt_input_basic(run_mocked_hook):
    output = run_mocked_hook(
        return_value={"tmp": "things"},
    )

    assert output == 'things'
