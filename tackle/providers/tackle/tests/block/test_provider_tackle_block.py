from tackle.main import tackle


def test_provider_system_hook_block_tackle(change_dir):
    """Simple block test."""
    output = tackle('merge.yaml', no_input=True)

    assert output['stuff'] == 'here'


def test_provider_system_hook_block_embedded_blocks(change_dir):
    """Embedded with multiple blocks."""
    output = tackle('embedded-blocks.yaml', no_input=True)

    assert output['stuff'] == 'things'
    assert output['blocker']['things'] == 'things'


def test_provider_system_hook_block_embedded_blocks_2(change_dir):
    """Complex block."""
    output = tackle('embedded-lists.yaml')
    assert output['one'][1]['two'][0]['three']


def test_provider_system_hook_block_looped(change_dir):
    """With a for loop."""
    output = tackle('looped.yaml', no_input=True)

    assert len(output['blocker']) == 2
    assert output['blocker'][0]['compact'] == 'stuff'
    assert output['blocker'][1]['compact'] == 'things'
    assert 'priv_expanded' not in output
    assert 'priv_compact' not in output


def test_provider_system_hook_block_block_merge(change_dir):
    """Block with a merge."""
    output = tackle('block-merge.yaml', no_input=True)
    # TODO: Update tests with https://github.com/robcxyz/tackle/issues/51
    # assert output['things'] == 'here'
    assert output['stuff'] == 'things'


def test_provider_system_hook_block_block(change_dir):
    """Complex block."""
    output = tackle('block.yaml', no_input=True)
    # TODO: Update tests with https://github.com/robcxyz/tackle/issues/51
    assert output['block']['things'] == 'here'


def test_provider_system_hook_block_list(change_dir):
    """Macro re-written block, simple."""
    output = tackle('list.yaml')
    assert output['public'] == ['stuff', 'things']
    assert 'private' not in output


def test_provider_system_hook_block_looped_context(change_dir):
    """Check that a temp context is built."""
    output = tackle('looped-context.yaml')
    assert len(output['networks']) == 2
    assert output['networks'][0]['network_name'] == 'foo'


def test_provider_system_hook_block_list_block(change_dir):
    """Complex block."""
    output = tackle('block-list.yaml')
    assert 'private' not in output


def test_provider_system_hook_block_logic(change_dir):
    """Block with logic."""
    output = tackle('block-logic.yaml')
    assert output


def test_provider_system_hook_block_tmp_context(change_dir):
    """Check that a temp context is built."""
    output = tackle('tmp-context.yaml')
    assert output['public']
