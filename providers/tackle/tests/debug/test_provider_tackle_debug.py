"""Tests dict input objects for `tackle.providers.tackle.block` module."""
from tackle.main import tackle


def test_provider_system_hook_debug():
    """Check we can call debug hook and output is not included."""
    output = tackle('basic.yaml', no_input=True)

    assert output == {'stuff': 'things'}


def test_provider_system_hook_debug_special_key():
    """Debug hook using special key."""
    output = tackle('special-key.yaml', no_input=True)

    assert 'debug' not in output
