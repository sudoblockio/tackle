from tackle import tackle


def test_provider_assert():
    """Check assertions."""
    output = tackle('assert.yaml')
    assert 'no_exist' not in output
    assert output['assert_lhs']
    assert not output['assert_lhs_false']
    assert output['assert_true']
    assert not output['assert_false']


def test_provider_assert_special_key():
    """Check assertions."""
    output = tackle('assert-special-key.yaml')
    assert output['assert']
