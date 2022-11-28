from tackle.main import tackle


def test_provider_prompt_checkbox_map_normal_no_input(change_dir):
    output = tackle('map_normal_checked.yaml', no_input=True)
    assert output['selection'] == ['stuff', 'things']


def test_provider_prompt_checkbox_map_no_input(change_dir):
    output = tackle('map_checked.yaml', no_input=True)
    assert output['selection'] == ['stuff', 'things']


def test_provider_prompt_checkbox_list_no_input(change_dir):
    output = tackle('list_checked.yaml', no_input=True)
    assert output['selection'] == ['stuff', 'things']


# # TODO: https://github.com/robcxyz/tackle/issues/46
# def test_provider_prompt_checkbox_list(change_dir, mocker):
#     mocker.patch(
#         'tackle.providers.prompts.hooks.checkbox.prompt',
#         return_value={"tmp": ["things"]},
#         autospec=True,
#     )
#
#     output = tackle('list.yaml')
#     assert output['selection'] == ['things']
#
#
# def test_provider_prompt_checkbox_list_index(change_dir, mocker):
#     mocker.patch(
#         'tackle.providers.prompts.hooks.checkbox.prompt',
#         return_value={"tmp": ["things"]},
#     )
#     output = tackle('list_index.yaml')
#     assert output['selection'] == [1]
#
#
# def test_provider_prompt_checkbox_map(change_dir, mocker):
#     mocker.patch(
#         'tackle.providers.prompts.hooks.checkbox.prompt',
#         return_value={"tmp": ["I do things"]},
#     )
#     output = tackle('map.yaml')
#     assert output['selection'] == ['things']
#
#
# def test_provider_prompt_checkbox_map_normal(change_dir, mocker):
#     mocker.patch(
#         'tackle.providers.prompts.hooks.checkbox.prompt',
#         return_value={"tmp": ["things"]},
#     )
#     output = tackle('map_normal.yaml')
#     assert output['selection'] == ['things']
#
#
# def test_provider_prompt_checkbox_map_index(change_dir, mocker):
#     mocker.patch(
#         'tackle.providers.prompts.hooks.checkbox.prompt',
#         return_value={"tmp": ["I do things"]},
#     )
#     output = tackle('map_index.yaml')
#     assert output['selection'] == [1]
