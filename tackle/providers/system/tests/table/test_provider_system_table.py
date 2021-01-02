# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.table` module."""
from tackle.main import tackle


def test_provider_system_hook_terraform(change_dir):
    """Verify the hook call works properly."""
    context = tackle('.', context_file='table_split.yaml', no_input=True)

    assert context
