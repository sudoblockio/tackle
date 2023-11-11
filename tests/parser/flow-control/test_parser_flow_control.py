import pytest

from tackle import tackle



@pytest.mark.parametrize("fixture", [
    'for-list-variable.yaml',
    'for-list-in-variable.yaml',
    'for-list-literal.yaml',
])
def test_parser_for_loop_list_parameterized(fixture):
    """Check for key with list variable."""
    o = tackle(fixture)
    assert o['expanded_value'] == ['bar', 'baz']
    assert o['expanded_index'] == [0, 1]
    assert o['compact'] == ['bar', 'baz']


@pytest.mark.parametrize("fixture", [
    'for-dict-variable.yaml',
    'for-dict-in-variable.yaml',
    'for-dict-literal.yaml',
])
def test_parser_for_loop_dict_parameterized(fixture):
    """Check for key with dict variable."""
    o = tackle(fixture)
    assert o['expanded_key'] == ['foo', 'baz']
    assert o['expanded_value'] == ['bar', 'bing']
    assert o['expanded_index'] == [0, 1]
    assert o['compact_key'] == ['foo', 'baz']
    assert o['compact_value'] == ['bar', 'bing']
    assert o['compact_index'] == [0, 1]
