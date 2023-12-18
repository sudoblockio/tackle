from tackle.main import tackle


def test_provider_tackle_hook_var():
    output = tackle('var.yaml')
    assert output['short'] == output['a_list']
    assert output['embed'] == "{{a_var_that_doesnt_exist}}"
    # TODO: Fix this - It should work when render by default is fixed
    # assert output['embed_bare'] == "tpl"
    assert output['list_of_lists'] == [[1, 2], [3, 4]]
    assert output['a_map_rendered']['stuff'] == 'things'


def test_provider_tackle_hook_var_statement():
    output = tackle('var-statement.yaml')
    assert output
