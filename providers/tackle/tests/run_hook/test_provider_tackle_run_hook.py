from tackle.main import tackle


def test_provider_tackle_run_hook():
    """Check run_hook."""
    output = tackle()
    assert output['expanded']['foo'] == 'baz'
    assert output['compact']['foo'] == 'baz'
