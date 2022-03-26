from tackle import tackle


def test_provider_assert(change_dir):
    """Check assertions."""
    output = tackle('assert.yaml')
    assert 'assert' in output
    assert 'no_exist' not in output
    assert output['assert_lhs']
