"""Tests dict input objects for `tackle.providers.system.hooks.var` module."""
from tackle.main import tackle


def test_provider_strings_split(change_dir):
    output = tackle('split.yaml')

    assert output['compact'] == output['expanded']
    assert output['compact'][0] == 'stuff'


def test_provider_strings_join(change_dir):
    output = tackle('join.yaml')

    assert output['a_str'] == ['things', 'stuffs']
    assert output['join_a_str'] == 'things.stuffs'
    # See test_render_hook_call_multiple for other test on this next assertion
    assert output['apath'] == "stuff.txt"
