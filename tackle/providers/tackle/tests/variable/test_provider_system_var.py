"""Tests dict input objects for `tackle.providers.system.hooks.variable` module."""
from tackle.main import tackle


def test_provider_system_hook_var(change_dir):
    """Verify the hook call works properly."""
    output = tackle('tackle.yaml')

    assert output['short'] == output['a_list']


def test_provider_system_hook_var_lists_embed(change_dir):
    """Verify the hook call works properly."""
    output = tackle('lists.yaml')

    assert output['list_of_lists'] == [[1, 2], [3, 4]]
