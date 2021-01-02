# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.path` module."""
import os
from tackle.main import tackle


def test_provider_system_hook_path(change_dir):
    """Verify the hook call works properly."""
    context = tackle('.', no_input=True, context_file='tackle.yaml')

    assert context['path_isdir']

    assert context['path_exists']
    assert os.path.exists(context['find_in_parent_dir'])  # Should be tests/tests...
    assert os.path.exists(context['find_in_parent_file'])
    assert context['find_in_parent_fallback'] == context['find_in_parent_dir']
