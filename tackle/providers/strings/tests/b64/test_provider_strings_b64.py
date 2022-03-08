from tackle.main import tackle


def test_provider_base64_code(change_dir):
    output = tackle()

    assert output['encode'] == output['encoded']
    assert output['decode'] == output['decoded']
