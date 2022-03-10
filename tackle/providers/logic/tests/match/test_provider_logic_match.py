"""Tests `import` in the `tackle.providers.tackle.hooks.match` hook."""
from tackle import tackle


def test_provider_system_hook_match(change_dir):
    """Run the source and check that the hooks imported the demo module."""
    context = tackle('loop.yaml')
    assert context['matches'][0]
    assert len(context['matches'][6]) == 2


def test_provider_system_hook_match_cases(change_dir):
    """Run the source and check that the hooks imported the demo module."""
    context = tackle('cases.yaml')
    assert context['matched_dict'] == 'this'
    assert context['fallback_dict'] == 'foo'
