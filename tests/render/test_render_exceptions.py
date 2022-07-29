import pytest

from tackle import exceptions, tackle

EXCEPTIONS = [
    (
        exceptions.UnknownTemplateVariableException,
        'unknown-variable.yaml',
        'is undefined',
    ),
    (
        exceptions.UnknownTemplateVariableException,
        'unknown-hook.yaml',
        'is the same as a hook and either',
    ),
    (
        exceptions.MissingTemplateArgsException,
        'hooks-args-wrong-type.yaml',
        'str type expected',
    ),
    (
        exceptions.MissingTemplateArgsException,
        'hooks-missing-args.yaml',
        '',
    ),
    (
        exceptions.TooManyTemplateArgsException,
        'hooks-args-too-many-args.yaml',
        '',  # TODO: Consider updating to better error
    ),
]


@pytest.mark.parametrize("exception,fixture,error_message", EXCEPTIONS)
def test_render_raise_error(change_curdir_fixtures, exception, fixture, error_message):
    with pytest.raises(exception) as e:
        tackle(fixture)

    assert error_message in e.value.message
