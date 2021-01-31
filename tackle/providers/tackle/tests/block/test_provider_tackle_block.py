# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.tackle.block` module."""
from tackle.main import tackle


def test_provider_system_hook_block_tackle(change_dir):
    """Verify the hook call works properly."""
    output = tackle('.', no_input=True)

    assert output['stuff'] == 'here'


def test_provider_system_hook_block_embedded_blocks(change_dir):
    """Verify the hook call works properly."""
    output = tackle('.', context_file='embedded_blocks.yaml', no_input=True)

    assert output['things'] == 'things'


def test_provider_system_hook_block_looped(change_dir):
    """Verify the hook call works properly."""
    output = tackle('.', context_file='looped.yaml', no_input=True)

    assert len(output['blocker']) == 2


def test_provider_system_hook_block_loop_empty(change_dir):
    """Verify the hook call works properly."""
    output = tackle('.', context_file='loop_empty.yaml', no_input=True)

    assert len(output['empty']) == 0


def test_provider_system_hook_block_block_merge(change_dir):
    """Verify the hook call works properly."""
    output = tackle('.', context_file='block_merge.yaml', no_input=True)

    assert output['things'] == 'here'
    assert output['foo'] == 'bar'


def test_provider_system_hook_block_block(change_dir):
    """Verify the hook call works properly."""
    output = tackle('.', context_file='block.yaml', no_input=True)

    assert output['block']['things'] == 'here'
    assert output['block']['foo'] == 'bar'
