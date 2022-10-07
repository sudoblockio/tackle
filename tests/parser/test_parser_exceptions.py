"""Test the input source part of the parser."""
import pytest

from tackle.exceptions import (
    EmptyTackleFileException,
    UnknownArgumentException,
    UnknownSourceException,
    HookParseException,
)

# from tackle import tackle
from tackle.cli import main

INPUT_SOURCES = [
    # TODO: empty should now be running help screen
    # ("empty-with-functions.yaml", EmptyTackleFileException),
    ("empty.yaml", EmptyTackleFileException),
    ("out-of-range-arg.yaml", UnknownArgumentException),
    ("non-existent.yaml", UnknownSourceException),
    ("hook-input-validation-error.yaml", HookParseException),
    ("function-input-validation-error.yaml", HookParseException),
]


@pytest.mark.parametrize("input_file,exception", INPUT_SOURCES)
def test_parser_raises_exceptions(chdir, input_file, exception):
    """Test raising exceptions."""
    chdir('exceptions')
    with pytest.raises(exception):
        main([input_file])
