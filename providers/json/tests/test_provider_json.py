from tackle import tackle


def test_provider_json():
    output = tackle('json.yaml')
    assert output
