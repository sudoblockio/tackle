from tackle import tackle


def test_provider_json(change_dir):
    output = tackle('json.yaml')
    assert output
