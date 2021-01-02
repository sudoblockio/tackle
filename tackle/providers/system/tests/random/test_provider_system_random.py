# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.random` module."""
from tackle.main import tackle


def test_provider_system_hook_random_string(change_dir):
    """Verify the hook call works properly."""
    output = tackle('.', no_input=True, context_file='tackle.yaml')

    assert len(output['random_hex']) == 8
    assert len(output['random_string']) == 8
