from tackle.main import tackle


def test_provider_console_print(change_dir):
    output = tackle('print.yaml')
    assert output


def test_provider_console_pprint(change_dir):
    output = tackle('pprint.yaml')
    assert 'this' in output
