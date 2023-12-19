import pytest

from providers.prompts.hooks.checkbox import InquirerCheckboxHook
from tackle import tackle


def test_provider_prompt_checkbox_map_normal_no_input():
    output = tackle('map_normal_checked.yaml', no_input=True)
    assert output['selection'] == ['stuff', 'things']


def test_provider_prompt_checkbox_map_no_input():
    output = tackle('map_checked.yaml', no_input=True)
    assert output['selection'] == ['stuff', 'things']


def test_provider_prompt_checkbox_list_no_input():
    output = tackle('list_checked.yaml', no_input=True)
    assert output['selection'] == ['stuff', 'things']


@pytest.fixture()
def run_mocked_hook(mocker, context):
    def f(return_value, **kwargs):
        # Patch the `prompt` method which is called by the hook and will since it
        # requires user input from terminal
        mocker.patch(
            'providers.prompts.hooks.checkbox.prompt', return_value=return_value
        )
        hook = InquirerCheckboxHook(**kwargs)
        output = hook.exec(context=context)

        return output

    return f


def test_provider_prompt_checkbox_list(run_mocked_hook):
    output = run_mocked_hook(
        return_value={"tmp": ["things"]},
        choices=['stuff', 'things'],
    )

    assert output == ['things']


def test_provider_prompt_checkbox_list_index(run_mocked_hook):
    output = run_mocked_hook(
        return_value={"tmp": ["things"]},
        choices=['stuff', 'things'],
        index=True,
    )

    assert output == [1]


def test_provider_prompt_checkbox_map(run_mocked_hook):
    output = run_mocked_hook(
        return_value={"tmp": ["stuff", "things"]},
        choices=['stuff', 'things'],
        checked=True,
    )

    assert output == ['stuff', 'things']


def test_provider_prompt_checkbox_map_normal(run_mocked_hook):
    output = run_mocked_hook(
        return_value={'tmp': ['foo', 'bar']},
        choices=[{'foo': 'stuff'}, {'bar': 'things'}],
        checked=True,
    )

    assert output == ['stuff', 'things']


def test_provider_prompt_checkbox_map_indexed(run_mocked_hook):
    output = run_mocked_hook(
        return_value={'tmp': ['foo']},
        choices=[{'foo': 'stuff'}, {'bar': 'things'}],
        index=True,
    )

    assert output == [0]
