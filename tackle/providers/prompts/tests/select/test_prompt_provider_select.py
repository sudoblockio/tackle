# from tackle import tackle
#
# # TODO: https://github.com/robcxyz/tackle/issues/46
#
#
# def test_provider_select_list_this(change_dir, mocker):
#     mocker.patch(
#         'tackle.providers.prompts.hooks.select.prompt', return_value={"tmp": "things"}
#     )
#     output = tackle('test.yaml')
#     assert output['selection'] == 'things'
#
#
# def test_provider_select_list(change_dir, mocker):
#     mocker.patch(
#         'tackle.providers.prompts.hooks.select.prompt', return_value={"tmp": "things"}
#     )
#     output = tackle('list.yaml')
#     assert output['selection'] == 'things'
#
#
# def test_provider_select_list_index(change_dir, mocker):
#     mocker.patch(
#         'tackle.providers.prompts.hooks.select.prompt', return_value={"tmp": "things"}
#     )
#     output = tackle('list_index.yaml')
#     assert output['selection'] == 1
#
#
# def test_provider_select_map(change_dir, mocker):
#     mocker.patch(
#         'tackle.providers.prompts.hooks.select.prompt',
#         return_value={"tmp": "I do things"},
#     )
#     output = tackle('map.yaml')
#     assert output['selection'] == 'things'
#
#
# def test_provider_select_map_index(change_dir, mocker):
#     mocker.patch(
#         'tackle.providers.prompts.hooks.select.prompt',
#         return_value={"tmp": "I do things"},
#     )
#     output = tackle('map_index.yaml')
#     assert output['selection'] == 1


# def test_provider_select_no_msg(change_dir, mocker):
#     mocker.patch(
#         'tackle.providers.prompts.hooks.select.prompt', return_value={"tmp": "things"}
#     )
#     output = tackle('no-msg.yaml')
#     assert output['selection'] == 'things'
