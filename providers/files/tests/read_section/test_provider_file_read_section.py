from tackle import tackle


def test_provider_system_hook_file_file():
    """Verify file hook can read a section within a file."""
    output = tackle('basic.yaml')
    assert output['foo'].startswith('foo:')
