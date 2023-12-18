import pytest

from tackle import exceptions, tackle

INPUT_SOURCES = [
    # TODO: empty should now be running help screen
    ("empty-hook-call.yaml", exceptions.UnknownArgumentException),
    ("out-of-range-arg.yaml", exceptions.UnknownTemplateVariableException),
    ("empty.yaml", exceptions.EmptyTackleFileException),
    ("non-existent.yaml", exceptions.UnknownSourceException),
    ("hook-input-validation-error.yaml", exceptions.HookParseException),
    ("function-input-validation-error.yaml", exceptions.HookParseException),
    ("for-none-type.yaml", exceptions.MalformedTemplateVariableException),
    ("top-level-hook-call.yaml", exceptions.TopLevelMergeException),
]


@pytest.mark.parametrize("input_file,exception", INPUT_SOURCES)
def test_parser_raises_exceptions(input_file, exception):
    """Test raising exceptions."""
    with pytest.raises(exception):
        tackle(input_file)


@pytest.mark.parametrize(
    "fixture",
    [
        'hook-native-bad-vars.yaml',
        'hook-native-missing.yaml',
    ],
)
def test_parser_exceptions_raise_native_hook_with_link_to_docs(fixture):
    """Make sure a link to the docs comes up for native hooks."""
    with pytest.raises(exceptions.HookParseException) as e:
        tackle(fixture)

    assert "https://sudoblockio.github.io/tackle/providers/Tackle/var/" in str(e)


FIELD_TYPE_EXCEPTION_FIXTURES = [
    ('str', 'str'),
    ('dict', 'str'),
    ('list', 'str'),
    ('str', 'type'),
    ('dict', 'type'),
    ('list', 'type'),
    ('str', 'default'),
    ('dict', 'default'),
    ('list', 'default'),
]


@pytest.mark.parametrize("type_,field_input", FIELD_TYPE_EXCEPTION_FIXTURES)
def test_hooks_raises_exceptions_field_types(cd, type_, field_input):
    """Check that a validation error is returned for each type of field definition."""
    cd('field-type-exceptions')
    with pytest.raises(exceptions.HookParseException):
        tackle(f'field-types-{type_}-error-{field_input}.yaml')
