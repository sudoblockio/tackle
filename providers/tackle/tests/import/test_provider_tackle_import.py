import pytest

from tackle import tackle
from tackle.factory import new_context
from tackle.models import Context
from tackle.parser import parse_context

FIXTURES = [
    'expanded-string.yaml',
    'expanded-list-dict.yaml',
    'local.yaml',
    'function-import.yaml',
]


@pytest.mark.parametrize("target", FIXTURES)
def test_provider_system_hook_import(target):
    """Run the source and check that the hooks imported the demo module."""
    context = new_context(target)
    # num_providers = len(context.provider_hooks.keys())
    num_providers = len(context.hooks.private.keys())
    parse_context(context=context)
    # assert num_providers < len(context.provider_hooks.keys())
    assert num_providers < len(context.private_hooks.keys())
    # assert 'tackle.providers.tackle-demos' in context.providers.hook_types


def test_provider_system_hook_import_local():
    """Assert local import of hook is valid."""
    o = tackle('local.yaml')
    assert o['stuff'] == 'thing'
