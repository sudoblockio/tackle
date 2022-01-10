"""Tests `import` in the `tackle.providers.tackle.hooks.match` hook."""
from tackle import tackle


def test_provider_system_hook_match(change_dir):
    """Run the source and check that the hooks imported the demo module."""
    context = tackle('values.yaml')
    assert 'assert' in context
