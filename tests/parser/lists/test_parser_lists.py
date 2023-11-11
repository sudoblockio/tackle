from tackle import tackle


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