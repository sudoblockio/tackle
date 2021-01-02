# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.listdir` module."""
from tackle.main import tackle


def test_provider_system_hook_command(change_dir):
    """Verify the hook call works properly."""
    output = tackle('.', no_input=True)

    assert len(output['string_input']) == 3
    assert len(output['string_input_sorted']) == 2
    assert len(output['list_input']['dirs/dir1']) == 2
