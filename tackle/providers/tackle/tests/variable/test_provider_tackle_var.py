from tackle.main import tackle


def test_provider_system_hook_var(change_dir):
    output = tackle('var.yaml')
    assert output['short'] == output['a_list']
    assert output['embed'] == "{{a_var_that_doesnt_exist}}"
    assert output['list_of_lists'] == [[1, 2], [3, 4]]
    assert output['a_map_rendered']['stuff'] == 'things'
