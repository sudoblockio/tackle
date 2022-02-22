import pytest
import os
import yaml

from tackle import tackle
from tackle.exceptions import EmptyBlockException

FIXTURES = [
    ('single-level.yaml', 'single-level-output.yaml'),
    ('nested-dict.yaml', 'nested-dict-output.yaml'),
    ('nested-for.yaml', 'nested-for-output.yaml'),
]


@pytest.mark.parametrize("input,output", FIXTURES)
def test_parser_blocks_validate_output(chdir, input, output):
    """Test blocks."""
    chdir(os.path.join("fixtures", "blocks"))
    with open(output) as f:
        expected_output = yaml.safe_load(f)

    tackle_output = tackle(input)
    assert tackle_output == expected_output


ERROR_SOURCES = [
    ("empty-block-exception.yaml", EmptyBlockException),
    # ("")
]


@pytest.mark.parametrize("input_file,exception", ERROR_SOURCES)
def test_parser_raises_exceptions(chdir, input_file, exception):
    """Validate that exceptions are raised."""
    chdir(os.path.join("fixtures", "blocks"))
    with pytest.raises(exception):
        tackle(input_file)


def test_parser_calling_directory_preserve(change_curdir_fixtures):
    """Validate that the calling_directory param is carried over from hook calls."""
    output = tackle('calling-context.yaml')
    assert output['call']['call']['calling_file'] == 'calling-context.yaml'
