"""Test the input source part of the parser."""
import pytest

from tackle import exceptions

# from tackle import tackle
from tackle.cli import main

INPUT_SOURCES = [
    # TODO: empty should now be running help screen
    # ("empty-with-functions.yaml", exceptions.EmptyTackleFileException),
    ("empty-hook-call.yaml", exceptions.HookCallException),
    ("empty.yaml", exceptions.EmptyTackleFileException),
    ("out-of-range-arg.yaml", exceptions.UnknownArgumentException),
    ("non-existent.yaml", exceptions.UnknownSourceException),
    ("hook-input-validation-error.yaml", exceptions.HookParseException),
    ("function-input-validation-error.yaml", exceptions.HookParseException),
]


@pytest.mark.parametrize("input_file,exception", INPUT_SOURCES)
def test_parser_raises_exceptions(chdir, input_file, exception):
    """Test raising exceptions."""
    chdir('exceptions-fixtures')
    with pytest.raises(exception):
        main([input_file])
