# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.tackle.block` module."""
from tackle.main import tackle


def test_provider_system_hook_debug(change_dir):
    """Verify the hook call works properly."""
    output = tackle('.', no_input=True)

    assert output['t'] == None
