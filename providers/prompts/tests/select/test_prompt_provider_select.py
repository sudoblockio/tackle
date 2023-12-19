import pytest

from providers.prompts.hooks.select import InquirerListHook


@pytest.fixture()
def run_mocked_hook(mocker, context):
    def f(return_value, **kwargs):
        # Patch the `prompt` method which is called by the hook and will since it
        # requires user input from terminal
        mocker.patch('providers.prompts.hooks.select.prompt', return_value=return_value)
        hook = InquirerListHook(**kwargs)
        output = hook.exec(context=context)

        return output

    return f


def test_provider_prompt_select_basic(run_mocked_hook):
    output = run_mocked_hook(
        return_value={'tmp': 'things'}, choices=['stuff', 'things']
    )

    assert output == 'things'


def test_provider_prompt_select_map(run_mocked_hook):
    output = run_mocked_hook(
        return_value={'tmp': 'foo'},
        choices=[{'foo': 'stuff'}, {'bar': 'things'}],
    )

    assert output == 'stuff'
