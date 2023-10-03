from tackle.main import tackle


def test_provider_console_print():
    output = tackle('print.yaml')
    assert output


def test_provider_console_pprint():
    output = tackle('pprint.yaml')
    assert 'this' in output
