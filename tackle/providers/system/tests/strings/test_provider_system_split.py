"""Tests dict input objects for `tackle.providers.system.hooks.var` module."""
from tackle.main import tackle


def test_provider_system_hook_split(change_dir):
    """Verify the hook call works properly."""
    output = tackle('tackle.yaml')

    assert output['a_str'] == ['things', 'stuffs']
    assert output['join_a_str'] == 'things.stuffs'
