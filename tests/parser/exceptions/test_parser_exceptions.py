import pytest

from tackle import tackle, exceptions

INPUT_SOURCES = [
    # TODO: empty should now be running help screen
    # ("empty-with-functions.yaml", exceptions.EmptyTackleFileException),
    ("empty-hook-call.yaml", exceptions.HookCallException),
    ("empty.yaml", exceptions.EmptyTackleFileException),
    ("out-of-range-arg.yaml", exceptions.UnknownArgumentException),
    ("non-existent.yaml", exceptions.UnknownSourceException),
    ("hook-input-validation-error.yaml", exceptions.HookParseException),
    ("function-input-validation-error.yaml", exceptions.HookParseException),
    ("for-none-type.yaml", exceptions.MalformedTemplateVariableException),
    # ("for-if.yaml", exceptions.MalformedTemplateVariableException),
]


@pytest.mark.parametrize("input_file,exception", INPUT_SOURCES)
def test_parser_raises_exceptions(input_file, exception):
    """Test raising exceptions."""
    with pytest.raises(exception):
        tackle(input_file)
