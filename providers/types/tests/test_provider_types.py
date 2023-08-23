from tackle import tackle


def test_provider_logic_type(change_dir):
    """Check type works."""
    output = tackle('type.yaml')
    assert output['str_type'] == 'str'
    assert output['list_type'] == 'list'
    assert output['a_dict_type'] == 'dict'
    assert output['dict_list_type'] == 'dict'
    assert output['list_dict_type'] == 'list'
    assert output['with_args']['type'] == 'list'
    assert output['default']['type'] == 'list'


def test_hook_casting(change_dir):
    """Check casting works."""
    output = tackle('castings.yaml')
    # Assertions in file
    assert output
