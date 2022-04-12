"""Tests `import` in the `tackle.providers.tackle.hooks.import` hook."""
import os

import pytest

from tackle import tackle
from tackle.models import Context
from tackle.parser import update_source

FIXTURES = [
    # # Handlers are experimental features
    # 'handler-str.yaml',
    # 'handler-list-compact.yaml',
    # 'expanded-string.yaml',
    # 'expanded-list-dict.yaml',
    'local.yaml',
    'function-import.yaml',
]


@pytest.mark.parametrize("target", FIXTURES)
def test_provider_system_hook_import(change_dir, target):
    """Run the source and check that the hooks imported the demo module."""
    context = Context(input_string=target)
    num_providers = len(context.provider_hooks.keys())
    update_source(context)
    assert num_providers < len(context.provider_hooks.keys())
    # assert 'tackle.providers.tackle-demos' in context.providers.hook_types


def test_provider_system_hook_import_local(change_dir):
    """Assert local import of hook is valid."""
    o = tackle('local.yaml')
    assert o['stuff'] == 'thing'


def test_provider_hook_import_func_provider_import(change_dir):
    """Assert local import of hook is valid."""
    os.chdir('func-provider')
    o = tackle()
    assert o['compact'] == 'a-default'
    assert o['jinja_extension_default'] == 'a-default'
    assert o['jinja_extension'] == 'things'
    assert o['jinja_filter'] == 'things'
