from tackle import tackle


def test_parser_conditionals_when():
    """Check `when` key which responds before `if` which works within a loop."""
    output = tackle('when.yaml')

    assert 'expanded' not in output


# # TODO: Fix this edge case where `if` can't be used with when
# #  https://github.com/sudoblockio/tackle/issues/216
# def test_parser_conditionals_when_if():
#     """Check `when` key is true with an `if` and loop."""
#     output = tackle('when-if.yaml')
#
#     assert len(output['expanded']) == 1


def test_parser_conditionals_else_str():
    """String values with `else`."""
    output = tackle('else-str.yaml')

    assert output['str'] == 'foo'
    assert output['compact'] == 'foo'
    assert output['str_render'] == 'things'
    assert output['str_render_block'] == 'things'


def test_parser_conditionals_else_dict():
    """Dict values for `else`."""
    output = tackle('else-dict.yaml')

    assert output['dict_render']['stuff'] == '{{stuff}}'
    assert output['dict_render_block'] == {'stuff': '{{stuff}}'}


def test_parser_conditionals_else_dict_empty():
    """Empty dict values for `else`."""
    output = tackle('else-dict-empty.yaml')

    assert output['dict_empty'] == {}
    assert output['dict_empty_block'] == {}
    assert output['dict_empty_block_list'][0]['do'] == {}


def test_parser_conditionals_else_hook_call():
    """Hook calls with `else`."""
    output = tackle('else-hook-call.yaml')

    assert output['hook_call']['stuff'] == 'things'
    assert output['embedded']['hook_call']['stuff'] == 'things'
    assert output['listed']['hook_call'][1]['stuff'] == 'things'
    assert output['block_listed']['block_call'][1]['stuff'] == 'things'


def test_parser_conditionals_else_dcl_hook():
    """Declarative hook calls with `else`."""
    output = tackle('else-dcl-hook.yaml')

    assert output['str'] == 'foo'
    assert output['dict_empty_block_list'][0]['do'] == {}
    assert output['hook_call']['stuff'] == 'things'


def test_parser_conditionals_list_comprehension():
    """Do a list comprehension where if responds within the loop."""
    output = tackle('list-comprehension.yaml')

    assert len(output['nodes']) == 1
