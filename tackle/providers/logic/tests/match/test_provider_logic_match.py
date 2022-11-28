import pytest
from tackle import tackle
from tackle.exceptions import HookCallException


def test_hook_match_loop(change_dir):
    """Run a loop of different match cases."""
    output = tackle('loop.yaml')
    # Assertions in fixture
    assert output


# TODO: https://github.com/robcxyz/tackle/issues/66
#  Add merge to loop functions
# def test_hook_match_block_loop(change_dir):
#     """Check that we can merge from a looped block into a looped match."""
#     output = tackle('block-loop.yaml')
#     # Assertions in fixture
#     assert output

# TODO: https://github.com/robcxyz/tackle/issues/66
#  Fix basic block macro functionality
# def test_hook_match_block_if(change_dir):
#     """Check that any kind of first level block makes sense."""
#     output = tackle('block-if.yaml')
#     # TODO: Assertions in fixture
#     assert output


def test_hook_match_cases(change_dir):
    """Run the source and check that the hooks imported the demo module."""
    output = tackle('cases.yaml')
    assert output['matched_dict'] == 'this'
    assert output['fallback_dict'] == 'foo'


def test_hook_match_value_list(change_dir):
    """
    Edge case where in match hooks one can have a single value trying to be merged into
    a temporary context which does not make sense.
    """
    output = tackle('value-list.yaml')
    # Assertions in file
    assert output


def test_hook_match_value_lists(change_dir):
    """
    Edge case where in match hooks one can have a single value trying to be merged into
    a temporary context which does not make sense.
    """
    o = tackle('lists.yaml')
    assert o


def test_hook_match_value_wrong_hook_type(change_dir):
    """
    Edge case where in match hooks one can have a single value trying to be merged into
    a temporary context which does not make sense.
    """
    with pytest.raises(HookCallException):
        tackle('wrong-hook-type.yaml')
