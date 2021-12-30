"""Tests dict input objects for `tackle.providers.rich.hooks.table` module."""
from tackle.main import tackle


def test_provider_system_hook_rich_table(change_dir):
    """Verify the hook call works properly."""
    output = tackle('table_split.yaml', no_input=True)
    assert 'table_split' in output
