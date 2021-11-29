"""Tests dict input objects for `tackle.providers.pyinquirer.hooks.confirm` module."""
from tackle.main import tackle


def test_provider_pyinquirer_confirm_hook(change_dir):
    """Verify the hook call works successfully."""
    o = tackle('tackle.yaml', no_input=True)
    assert 'this' in o
