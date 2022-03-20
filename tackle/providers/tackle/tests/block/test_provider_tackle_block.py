from tackle.main import tackle


def test_provider_system_hook_block_tackle(change_dir):
    """Simple block test."""
    output = tackle('merge.yaml', no_input=True)

    assert output['stuff'] == 'here'

    # assert 'things' not in output


def test_provider_system_hook_block_embedded_blocks(change_dir):
    """Embedded with multiple blocks."""
    output = tackle('embedded_blocks.yaml', no_input=True)

    assert output['stuff'] == 'things'
    assert output['blocker']['things'] == 'things'


def test_provider_system_hook_block_looped(change_dir):
    """With a for loop."""
    output = tackle('looped.yaml', no_input=True)

    assert len(output['blocker']) == 2
    assert output['blocker'][0]['first'] == 'stuff'
    assert output['blocker'][1]['first'] == 'things'


def test_provider_system_hook_block_block_merge(change_dir):
    """Block with a merge."""
    output = tackle('block_merge.yaml', no_input=True)

    assert output['things'] == 'here'


def test_provider_system_hook_block_block(change_dir):
    """Complex block."""
    output = tackle('block.yaml', no_input=True)

    assert output['block']['things'] == 'here'
    assert output['block']['foo'] == 'bar'


def test_provider_system_hook_block_list(change_dir):
    """Complex block."""
    output = tackle('list.yaml')
    assert 'private' not in output
