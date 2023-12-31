import pytest

from tackle import exceptions, tackle


@pytest.mark.parametrize(
    "file_name",
    [
        'expanded.yaml',
        'expanded-after.yaml',
        'dict-parse.yaml',
        'compact.yaml',
        'compact-context.yaml',
        'compact-default.yaml',
        'type-union.yaml',
        'full.yaml',
        'key-field-name.yaml',
    ],
)
def test_hooks_validators_expanded(file_name):
    output = tackle(file_name)

    assert output['call']['foo'] == 'bar'
    assert output['error'] == 1


def test_hooks_validators_complex_types():
    output = tackle('complex-types.yaml')

    assert output['call']['foo'] == '1.1.1.1'
    assert output['error'] == 1


def test_hooks_validators_composed_type():
    output = tackle('composed-type.yaml')

    assert output['call']['foo'] == '1.1.1.1'
    assert output['error'] == 1


def test_hooks_validators_error_mode():
    """Mode should be `before`, `after`, or `wrap`."""
    with pytest.raises(exceptions.MalformedHookFieldException):
        tackle('error-mode.yaml')


def test_hooks_validators_error_body_or_extra():
    """Validator can have body or extra but not both."""
    with pytest.raises(exceptions.MalformedHookFieldException):
        tackle('error-body-or-extra.yaml')
