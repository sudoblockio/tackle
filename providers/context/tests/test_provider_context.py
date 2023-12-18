from tackle import tackle


def test_provider_system_hook_dicts_update():
    output = tackle('update.yaml')
    assert output['update_map'] == output['arg']
    # TODO: https://github.com/sudoblockio/tackle/issues/192
    #  Determine if update hook copies data
    # assert output['update_map2'] == output['arg2']
    assert output['dict_map'] == {'foo': 'bar', 'bar': 'bar'}
    assert output['input_map']['foo'] == 'bing'
    assert output['new_list'][2] == 'baz'
    assert output['new_str'] == 'baz'


def test_provider_system_hook_dicts_update_reference():
    """Show that references are preserved when updating a dict in place."""
    # TODO: https://github.com/sudoblockio/tackle/issues/192
    #  Determine if update hook copies data
    output = tackle('update-reference.yaml')
    assert output['update_map']['stuff']['foo'] == 'bar'


def test_provider_system_hook_dicts_pop():
    output = tackle('pop.yaml')
    assert 'stuff' not in output['pop_map']
    assert output['arg_1'] == ['stuff']
    assert 'foo' not in output['arg_2']
    assert 'baz' in output['arg_2']


def test_provider_system_hook_dicts_pop_data():
    """
    Check we can mutate the data in the context.
    See https://github.com/pydantic/pydantic/issues/7390
    Have issue with pydantic 1.x to 2.x
    """
    output = tackle('pop-in-place.yaml')
    assert output['embedded']['list'] == ['stuff']
    assert output['list'] == ['things']


def test_provider_system_hook_dicts_keys():
    """Validated keys hook outputs list from map."""
    output = tackle('keys.yaml')
    # Validated with inline assertions
    assert output['output'] == ['stuff', 'things']
    assert output['check']
    assert output['check_key_path']


def test_provider_system_hook_dicts_values():
    """Validated keys hook outputs list from map."""
    output = tackle('values.yaml')
    # Validated with inline assertions
    assert output['output']
    assert output['check']
    assert output['check_key_path']


def test_provider_context_set():
    """Check that we can set keys."""
    output = tackle('set.yaml')

    assert output['one'][0]['that']['stuff'] == 'more things'
    assert output['two'][0]['that']['stuff'] == 'more things'
    assert output['three'][0]['that']['stuff'] == 'more things'


def test_provider_context_set_loop():
    """Check that we can set keys."""
    output = tackle('set-in-loop.yaml')

    assert output


def test_provider_context_get():
    """Check that we can get keys."""
    output = tackle('get.yaml')
    assert output['getter_list'] == 'things'
    assert output['getter_str'] == 'things'
    assert output['getter_str_sep'] == 'things'


def test_provider_context_delete():
    """Check that we can delete keys."""
    output = tackle('delete.yaml')
    assert output['one'][0]['that'] == {}
    assert output['two'][0]['that'] == {}
    assert output['three'][0]['that'] == {}


def test_provider_context_append():
    """Verify the append hook literal and in place."""
    output = tackle('append.yaml')
    expected_output = ['stuff', 'things', 'foo']

    assert 'donkey' in output['appended_list']
    assert output['output'] == expected_output
    assert output['path']['to']['list'] == expected_output


# # TODO: Fix appending from within a block
# #  https://github.com/sudoblockio/tackle/issues/220
# def test_provider_context_append_block():
#     """Verify the append hook literal and in place."""
#     output = tackle('append-block.yaml')
#
#     assert 'private' not in output
#     assert len(output['stuff']) == 2


def test_provider_context_append_dcl_hook():
    """Check that we can append within a dcl hook."""
    output = tackle('append-dcl-hook.yaml')
    assert output['call']['output'] == ['fizz']
