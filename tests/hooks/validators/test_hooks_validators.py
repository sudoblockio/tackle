import pytest

from tackle import tackle, exceptions

@pytest.mark.parametrize("file_name", [
    'expanded.yaml',
    'expanded-after.yaml',
    'compact.yaml',
])
def test_hooks_validators_expanded(file_name):
    output = tackle(file_name)
    assert output['call']['foo'] == 'bar'
    assert output['error'] == 1


def test_hooks_validators_error_mode():
    """Mode should be `before`, `after`, or `wrap`."""
    with pytest.raises(exceptions.MalformedHookFieldException):
        tackle('error-mode.yaml')


def test_hooks_validators_error_body_or_extra():
    """Validator can have body or extra but not both."""
    with pytest.raises(exceptions.MalformedHookFieldException):
        tackle('error-body-or-extra.yaml')