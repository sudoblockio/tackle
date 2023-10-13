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
        'unknown-dcl-hook.yaml',
        'is the same as a hook and either',
    ),
    (
        exceptions.UnknownTemplateVariableException,
        'unknown-python-hook.yaml',
        'is the same as a hook and either',
    ),
    (
        exceptions.MissingTemplateArgsException,
        'hooks-args-wrong-type.yaml',
        'Input should be a valid string',
    ),
    (
        exceptions.MissingTemplateArgsException,
        'hooks-missing-args.yaml',
        '',
    ),
    # (
    #     exceptions.TooManyTemplateArgsException,
    #     'hooks-args-too-many-args.yaml',
    #     '',  # TODO: RM since this is an effect of joining remaining args that are str
    # ),
]


@pytest.mark.parametrize("exception,fixture,error_message", EXCEPTIONS)
def test_render_raise_error(cd_fixtures, exception, fixture, error_message):
    with pytest.raises(exception) as e:
        tackle(fixture)

    assert error_message in e.value.message
