import pytest

from tackle import exceptions, tackle

@pytest.mark.parametrize("exception,fixture,error_message", [
    (
        exceptions.UnknownTemplateVariableException,
        'unknown-variable.yaml',
        'Could not find one of',
    ),
    (
        exceptions.MalformedTemplateVariableException,
        'uncalled-dcl-hook.yaml',
        'try calling',
    ),
    (
        exceptions.MalformedTemplateVariableException,
        'uncalled-python-hook.yaml',
        'try calling',
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
])
def test_render_raise_error(cd_fixtures, exception, fixture, error_message):
    with pytest.raises(exception) as e:
        tackle(fixture)

    assert error_message in e.value.message
