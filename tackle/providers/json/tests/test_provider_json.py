"""Tests `import` in the `tackle.providers.tackle.hooks.match` hook."""
from tackle import tackle


def test_provider_system_hook_match(change_dir):
    """Check assertions."""
    output = tackle('json.yaml')
    assert output
