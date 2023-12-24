from tackle import tackle
from tackle.utils.hooks import get_hook


def test_provider_json():
    output = tackle('json.yaml')
    assert output


def test_provider_json_encode():
    Hook = get_hook('json_encode')
    output = Hook(data={"Section1": {"keyA": "valueA", "keyB": "valueB"}}).exec()
    assert output == '{"Section1": {"keyA": "valueA", "keyB": "valueB"}}'


def test_provider_json_decode():
    Hook = get_hook('json_decode')
    output = Hook(data='{"Section1": {"keyA": "valueA", "keyB": "valueB"}}').exec()
    assert output == {"Section1": {"keyA": "valueA", "keyB": "valueB"}}
