# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.print` module."""
from tackle.main import tackle


def test_provider_system_hook_print(change_dir):
    """Verify the hook call works properly."""
    output = tackle(no_input=True, context_file='print.yaml')
    assert output['md']
    assert output['this'] == 'this'
    assert output['multiline'] == 'this'
