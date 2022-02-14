from tackle.main import tackle


def test_provider_prompt_checkbox_list(change_dir, mocker):
    mocker.patch(
        'tackle.providers.prompts.hooks.checkbox.prompt',
        return_value={"tmp": ["things"]},
    )
    output = tackle('list.yaml')
    assert output['selection'] == ['things']


def test_provider_prompt_checkbox_list_index(change_dir, mocker):
    mocker.patch(
        'tackle.providers.prompts.hooks.checkbox.prompt',
        return_value={"tmp": ["things"]},
    )
    output = tackle('list_index.yaml')
    assert output['selection'] == [1]


def test_provider_prompt_checkbox_map(change_dir, mocker):
    mocker.patch(
        'tackle.providers.prompts.hooks.checkbox.prompt',
        return_value={"tmp": ["I do things"]},
    )
    output = tackle('map.yaml')
    assert output['selection'] == ['things']


def test_provider_prompt_checkbox_map_normal(change_dir, mocker):
    mocker.patch(
        'tackle.providers.prompts.hooks.checkbox.prompt',
        return_value={"tmp": ["things"]},
    )
    output = tackle('map_normal.yaml')
    assert output['selection'] == ['things']


def test_provider_prompt_checkbox_map_index(change_dir, mocker):
    mocker.patch(
        'tackle.providers.prompts.hooks.checkbox.prompt',
        return_value={"tmp": ["I do things"]},
    )
    output = tackle('map_index.yaml')
    assert output['selection'] == [1]
