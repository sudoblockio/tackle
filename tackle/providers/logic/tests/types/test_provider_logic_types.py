"""Tests `import` in the `tackle.providers.tackle.hooks.match` hook."""
from tackle import tackle


def test_provider_logic_type(change_dir):
    """Check assertions."""
    output = tackle('type.yaml')
    assert output['str_type'] == 'str'
    assert output['list_type'] == 'list'
    assert output['a_dict_type'] == 'dict'
    assert output['dict_list_type'] == 'dict'
    assert output['list_dict_type'] == 'list'
