from tackle import tackle


def test_parser_lists_list_hooks():
    """"""
    o = tackle('list-hooks.yaml')
    assert o[0] == 'foo'
    assert o[1] == {'foo': 'foo'}
    assert o[2] == {'foo': {'bar': 'foo'}}


def test_parser_lists_list_false_conditionals():
    """
    When there is a list of hooks and the conditions are false we expect that the list
     is empty.
    """
    o = tackle('list-false-conditionals.yaml')

    assert o['a_list'] == []


def test_parser_lists_list_hook_render():
    """When we have a list of renderables in marked with a hook we render the list."""
    o = tackle('list-hook-render.yaml')

    assert o['a_list'] == ['bar', 'things']
