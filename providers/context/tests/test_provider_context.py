from tackle import tackle


def test_provider_system_hook_dicts_update(change_dir):
    output = tackle('update.yaml')
    assert output['update_map'] == output['arg']
    assert output['update_map2'] == output['arg2']
    assert output['dict_map'] == {'foo': 'bar', 'bar': 'bar'}
    assert output['input_map']['foo'] == 'bing'
    assert output['new_list'][2] == 'baz'
    assert output['new_str'] == 'baz'


def test_provider_system_hook_dicts_update_2(change_dir):
    output = tackle('update-2.yaml')
    assert output


def test_provider_system_hook_dicts_pop(change_dir):
    output = tackle('pop.yaml')
    assert 'stuff' not in output['pop_map']
    assert output['arg_1'] == ['stuff']
    assert 'foo' not in output['arg_2']
    assert 'baz' in output['arg_2']
    assert output['embedded']['list'] == ['stuff']
    assert output['list'] == ['things']


def test_provider_system_hook_dicts_keys(change_dir):
    """Validated keys hook outputs list from map."""
    output = tackle('keys.yaml')
    # Validated with inline assertions
    assert output['output'] == ['stuff', 'things']
    assert output['check']
    assert output['check_key_path']


def test_provider_system_hook_dicts_values(change_dir):
    """Validated keys hook outputs list from map."""
    output = tackle('values.yaml')
    # Validated with inline assertions
    assert output['output']
    assert output['check']
    assert output['check_key_path']


def test_provider_context_set(change_dir):
    """Check that we can set keys."""
    output = tackle('set.yaml')
    assert output['one'][0]['that']['stuff'] == 'more things'
    assert output['two'][0]['that']['stuff'] == 'more things'
    assert output['three'][0]['that']['stuff'] == 'more things'


def test_provider_context_get(change_dir):
    """Check that we can get keys."""
    output = tackle('get.yaml')
    assert output['getter_list'] == 'things'
    assert output['getter_str'] == 'things'
    assert output['getter_str_sep'] == 'things'


def test_provider_context_delete(change_dir):
    """Check that we can delete keys."""
    output = tackle('delete.yaml')
    assert output['one'][0]['that'] == {}
    assert output['two'][0]['that'] == {}
    assert output['three'][0]['that'] == {}


def test_provider_context_append(change_dir):
    """Verify the append hook literal and in place."""
    output = tackle('append.yaml')
    assert 'donkey' in output['appended_list']
    expected_output = ['stuff', 'things', 'foo']
    assert output['output'] == expected_output
    assert output['path']['to']['list'] == expected_output
    assert len(output['stuff']) == 2


def test_provider_context_append_dict(change_dir):
    """Verify the append hook literal and in place."""
    output = tackle('append-dict.yaml')
    assert output
