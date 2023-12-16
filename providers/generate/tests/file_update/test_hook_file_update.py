from tackle import tackle


def test_hook_file_update():
    output = tackle('file_update.yaml')
    assert output
