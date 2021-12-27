"""Test the input source part of the parser."""
import pytest

from tackle.exceptions import EmptyTackleFileException

INPUT_SOURCES = [("empty.yaml", EmptyTackleFileException)]


@pytest.mark.parametrize("input_file,exception", INPUT_SOURCES)
def test_parser_raises_exceptions(
    change_curdir_fixtures, cli_runner, input_file, exception
):
    with pytest.raises(exception):
        cli_runner(input_file)
