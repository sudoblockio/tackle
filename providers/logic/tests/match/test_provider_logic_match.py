import pytest

from tackle import exceptions, tackle


def test_hook_match_loop():
    """Run a loop of different match cases."""
    output = tackle('loop.yaml')
    assert output["matches"][0]
    assert isinstance(output["matches"][0], bool)
    assert output["matches"][1] == {'stuff': 'things'}
    assert output["matches"][2] == ['stuff', 'things']
    assert output["matches"][3]['a_dict'] == {'stuff': 'things'}
    assert output["matches"][3]['list'] == ['stuff', 'things']
    assert output["matches"][4] == 'expanded'
    assert output["matches"][5] == 'compact'


def test_hook_match_block_match_block():
    """Check that we can maintain correct context with match in nested blocks."""
    output = tackle('block-match-block.yaml')
    assert len(output['block']) == 5  # 5 keys
    assert output['block']['matches']['render_inner'] == 'bar'
    assert output['block']['render_inner'] == 'things'

    assert output['block_loop']['matches'][0]['render_inner'] == 'bar'
    assert output['block_loop']['matches'] == output['block_loop']['check']


def test_hook_match_block_loop_match_block():
    """Check that we can merge from a looped block into a looped match."""
    # TODO: Fix me next version....
    #  https://github.com/sudoblockio/tackle/issues/267
    #  Could not find one of `matches` in the context, Exiting...
    #  Looks like something to do with the temp data not being reset which is an
    #  artifact of the current broken memory model. Won't fix till next version
    output = tackle('block-loop-match-block.yaml')
    assert len(output['block']) == 2
    assert output['block'][0]['matches']['foo'] == 'bar'

    assert output['block_loop'][0]['matches'][0]['foo'] == 'bar'
    assert output['block_loop'][0]['matches'][1]['iter'] == 4
    assert output['block_loop'][1]['matches'][0]['iter'] == 3


def test_hook_match_case_dict():
    """Make sure dicts without plain arrows in key are simply passed."""
    output = tackle('case-dict.yaml')
    assert output['matches']['foo->'] == "{{bar}}"


def test_hook_match_case_block_loop():
    """Check that we can do match within a loop of a block."""
    o = tackle('case-block-loop.yaml')
    # Assertions in file
    assert o


def test_hook_match_case_block():
    """Check that we can do match within a loop of a block."""
    o = tackle('case-block.yaml')
    # Assertions in file
    assert o


def test_hook_match_case_block_if():
    """Check that any kind of first level block makes sense."""
    output = tackle('case-block-if.yaml')
    # Assertions in fixture
    assert output
    # TODO: https://github.com/sudoblockio/tackle/issues/159
    #  `match` hook  with `block` + false `if` should set empty map
    # assert output['matches_false'] == {}


def test_hook_match_case_dict_hooks():
    """Check that with dicts we can render hooks."""
    output = tackle('case-dict-hooks.yaml')
    # Assertions in file
    assert output


# # TODO: Fix losing reference to the HookCallInput
# #  https://github.com/sudoblockio/tackle/issues/184
# def test_hook_match_case_block_merge():
#     """
#     Check that we can do a merge from a block which is the same as a merge from top
#      level hook call.
#     """
#     o = tackle('case-block-merge.yaml')
#     assert o['foo'] == 'bar'
#     assert o['bar'] == 'bar'
#     assert len(o) == 3


def test_hook_match_cases():
    """Validate that regex matches work."""
    output = tackle('cases.yaml')
    assert output['matched_dict'] == 'this'
    assert output['fallback_dict'] == 'foo'


def test_hook_match_default_underscore():
    """Check that we can have an underscore for the default case."""
    o = tackle('default-underscore.yaml')

    assert o['normal_str'] == 'foo'
    assert o['normal_dict']['foo'] == 'bar'
    assert o['hook_call'] == 'foo'
    # TODO: Determine if `match` hook should parse dictionaries by default
    #  https://github.com/sudoblockio/tackle/issues/160
    assert o['normal_dict_hook']['stuff']['->'] == 'literal things'


def test_hook_match_default_hook():
    """Check that we can have a hook for the default case."""
    o = tackle('default-hook.yaml')
    assert o['normal_dict'] == 'bar'
    assert o['normal_dict_hook']['foo'] == 'foo'
    # TODO: Determine if `match` hook should parse dictionaries by default
    #  https://github.com/sudoblockio/tackle/issues/160
    # assert o['normal_dict_hook']['stuff'] == 'stuff'


def test_hook_match_value_lists():
    """Check we can match a list."""
    o = tackle('lists.yaml')
    # Assertions in file
    assert o


def test_hook_match_render_key():
    """Check we can render keys in a match statement."""
    o = tackle('render-key.yaml')

    assert o['value'] == 'foo'
    assert o['hook_call'] == 'foo'


def test_hook_match_render_bool_no_value():
    """Check we can render keys in a match statement."""
    o = tackle('render-no-value.yaml')

    assert o['1'] == 1
    assert o['3'] == "fizz"
    assert o['5'] == "buzz"
    assert o['15'] == "fizzbuzz"


def test_hook_match_bool_match():
    """Check we can render keys in a match statement."""
    o = tackle('bool-match.yaml')

    assert o['render_single']
    assert o['render_with_multiple']


def test_hook_match_error_malformed_regex():
    """Validate that errors are caught appropriately for bad regex."""
    with pytest.raises(exceptions.HookCallException):
        tackle('error-malformed-regex.yaml')


def test_hook_match_error_wrong_hook_type():
    """Check that when a non-hook is called like a hook that it errors gracefully."""
    with pytest.raises(exceptions.HookCallException):
        tackle('error-wrong-hook-type.yaml')


def test_hook_match_error_non_existent_key():
    """Error when no key exists."""
    with pytest.raises(exceptions.HookCallException):
        tackle('error-non-existent-key.yaml')


def test_hook_match_error_block_loop_merge():
    """Get error when we try to merge a list into a dict."""
    with pytest.raises(exceptions.AppendMergeException):
        tackle('error-block-loop-merge.yaml')
