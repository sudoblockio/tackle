# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.block` module."""
import os
from tackle.main import tackle


def test_provider_system_hook_block_(change_dir):
    """Verify the hook call works properly."""

    output = tackle('.', no_input=True)

    assert output['stuff'] == 'here'

    output = tackle('.', context_file='embedded_blocks.yaml', no_input=True,)

    assert output['things'] == 'things'

    output = tackle('.', context_file='looped.yaml', no_input=True,)

    assert len(output['blocker']) == 2

    output = tackle('.', context_file='block_nuki.yaml', no_input=True,)

    assert output['things'] == 'things'
