from tackle.main import tackle
from tackle.utils.hooks import get_hook


def test_provider_toml_hook_read():
    o = tackle('read.yaml', no_input=True)
    assert 'owner' in o['read'].keys()


def test_provider_toml_decode():
    Hook = get_hook('toml_decode')
    output = Hook(data='[Section1]\nkeyA = "valueA"\nkeyB = "valueB"\n').exec()
    assert output == {"Section1": {"keyA": "valueA", "keyB": "valueB"}}
