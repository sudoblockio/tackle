"""Tests `import` in the `tackle.providers.tackle.hooks.match` hook."""
from tackle import tackle


def test_hook_match_loop(change_dir):
    """Run the source and check that the hooks imported the demo module."""
    output = tackle('loop.yaml')
    assert output['matches'][0]
    assert len(output['matches'][6]) == 2


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
