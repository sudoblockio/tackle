"""Tests dict input objects for `tackle.providers.tackle.block` module."""
from tackle.main import tackle


def test_provider_system_hook_block_tackle(change_dir):
    """Verify the hook call works properly."""
    output = tackle('basic.yaml', no_input=True)

    assert output['stuff'] == 'here'
    assert 'things' not in output


def test_provider_system_hook_block_embedded_blocks(change_dir):
    """Verify the hook call works properly."""
    output = tackle('embedded_blocks.yaml', no_input=True)

    assert output['things'] == 'things'


def test_provider_system_hook_block_looped(change_dir):
    """Verify the hook call works properly."""
    output = tackle('looped.yaml', no_input=True)

    assert len(output['blocker']) == 2


def test_provider_system_hook_block_block_merge(change_dir):
    """Verify the hook call works properly."""
    output = tackle('block_merge.yaml', no_input=True)

    assert output['things'] == 'here'
    assert output['foo'] == 'bar'


def test_provider_system_hook_block_block(change_dir):
    """Verify the hook call works properly."""
    output = tackle('block.yaml', no_input=True)

    assert output['block']['things'] == 'here'
    assert output['block']['foo'] == 'bar'
