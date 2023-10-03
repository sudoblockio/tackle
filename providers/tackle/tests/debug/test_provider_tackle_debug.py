"""Tests dict input objects for `tackle.providers.tackle.block` module."""
from tackle.main import tackle


def test_provider_system_hook_debug():
    output = tackle(no_input=True)

    assert output['t'] is None
    assert 'g' not in output
