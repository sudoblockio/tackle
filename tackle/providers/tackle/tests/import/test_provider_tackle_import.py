"""Tests `import` in the `tackle.providers.tackle.hooks.import` hook."""
import pytest

from tackle.models import Context
from tackle.parser import update_source

FIXTURES = [
    # # Handlers are experimental features
    # 'handler-str.yaml',
    # 'handler-list-compact.yaml',
    'expanded-string.yaml',
    'expanded-list-dict.yaml',
]


@pytest.mark.parametrize("target", FIXTURES)
def test_provider_system_hook_import(change_dir, target, mocker):
    """Run the source and check that the hooks imported the demo module."""
    context = Context(input_string=target)
    num_providers = len(context.providers.hook_types)
    update_source(context)
    assert num_providers < len(context.providers.hook_types)
    # assert 'tackle.providers.tackle-demos' in context.providers.hook_types
