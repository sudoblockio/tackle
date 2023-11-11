from tackle import tackle


def test_hooks_extends_str():
    """Check that we can extend a base function."""
    output = tackle('extends.yaml')
    assert output['t'] == ['hello', 'world']


def test_hooks_extends_list():
    """Check that we can extend a base function with a list of other functions."""
    output = tackle('extends-list.yaml')
    assert output['t'] == ['hello', 'dude']


def test_hooks_extends_method():
    """Check that we can extend a base function with a list of other functions."""
    output = tackle('extends-method.yaml')
    assert output['t']
