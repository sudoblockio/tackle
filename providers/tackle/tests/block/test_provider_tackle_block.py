from tackle.main import tackle


def test_provider_system_hook_block_block():
    """Complex block."""
    output = tackle('block.yaml', no_input=True)

    assert output['block']['things'] == 'here'
    assert output['block']['test_block']


def test_provider_system_hook_block_tackle():
    """Simple block test."""
    output = tackle('merge.yaml')

    assert output['things'] == 'here'
    assert output['stuff'] == 'here'
    assert 'not_things' not in output


def test_provider_system_hook_block_embedded_blocks():
    """Embedded with multiple blocks."""
    output = tackle('embedded-blocks.yaml', no_input=True)

    assert output['stuff'] == 'things'
    assert output['blocker']['things'] == 'things'
    assert output['blocker']['test_block']['my_dog'] == 'dog'
    assert output['blocker']['test_block']['my_public_dog'] == 'dog'


def test_provider_system_hook_block_embedded_lists():
    """Complex block."""
    output = tackle('embedded-lists.yaml')
    assert output['one'][1]['two'][0]['three']


def test_provider_system_hook_block_looped():
    """With a for loop."""
    output = tackle('looped.yaml')

    assert len(output['blocker']) == 2
    assert output['blocker'][0]['compact'] == 'stuff'
    assert output['blocker'][1]['compact'] == 'things'
    assert 'priv_expanded' not in output
    assert 'priv_compact' not in output


def test_provider_system_hook_block_block_merge():
    """Block with a merge."""
    output = tackle('block-merge.yaml')

    assert output['test_block']['my_dog'] == 'things'
    assert output['test_block_macro']['my_dog'] == 'things'
    assert len(output) == 3


# TODO: The error here is that context.data.existing is not properly flushed between
#  runs. When we are in the second object (ie block1_nested) we still get data from
#  the prior execution.
def test_hook_block_block_loop_block():
    """Make sure we preserve the temporary context from nested blocks."""
    output = tackle('block-loop-block.yaml')

    assert output['block1'][0]['block2']['foo'] == 'bar'
    assert output['block1_nested'][0]['block2']['foo']['bar'] == 'baz'
    assert len(output['block1_nested']) == 2


def test_provider_system_hook_block_list():
    """Macro re-written block, simple."""
    output = tackle('list.yaml')

    assert output['public'] == ['stuff', 'things']
    assert 'private' not in output


def test_parser_list_to_block_macro():
    """Check what lists do in a block."""
    output = tackle('list-block.yaml')

    assert isinstance(output['expanded'][1], list)


def test_provider_system_hook_block_looped_context():
    """Check that a temp context is built."""
    output = tackle('looped-context.yaml')
    assert len(output['networks']) == 2
    assert output['networks'][0]['network_name'] == 'foo'


def test_provider_system_hook_block_list_block():
    """Complex block."""
    output = tackle('block-list.yaml')
    assert 'private' not in output


def test_provider_system_hook_block_logic():
    """Block with logic."""
    output = tackle('block-logic.yaml')
    assert output['block_true']['friend']
    assert 'block' not in output


def test_provider_system_hook_block_tmp_context():
    """Check that a temp context is built."""
    output = tackle('tmp-context.yaml')
    assert output['public']['that']


def test_provider_system_hook_block_key_list():
    """
    Check that a temp context is with copies of mutable objects - bug before where the
     same list was being appended to in public and temporary data causing duplicate
     values.
    """
    output = tackle('key-list.yaml')

    assert output == {'ablock': {'foo': ['bar', 'baz']}}


def test_provider_tackle_block_chdir():
    """Check that we can use base methods like chdir in a block."""
    output = tackle('chdir.yaml')

    assert output['foo']['do']['stuff'] == 'here'
