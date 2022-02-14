from tackle.main import tackle


def test_provider_system_hook_random_string(change_dir):
    output = tackle('random.yaml')

    assert len(output['random_hex']) == 8
    assert len(output['random_hex_arg']) == 4
    assert len(output['random_string']) == 8
    assert len(output['random_string_arg']) == 6
    assert output['random_string_upper_arg'].isupper()
