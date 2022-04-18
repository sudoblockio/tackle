import pytest
import os

from tackle import tackle
from tackle.utils.files import read_config_file
from tackle.exceptions import EmptyBlockException

FIXTURES = [
    ('single-level.yaml', 'single-level-output.yaml'),
    ('nested-dict.yaml', 'nested-dict-output.yaml'),
    ('nested-for.yaml', 'nested-for-output.yaml'),
    # Consider RM - Too much stuff
    # ('ansible-parse-call.yaml', 'ansible-parse-output.yaml')
]


@pytest.mark.parametrize("input,output", FIXTURES)
def test_parser_blocks_validate_output(chdir, input, output):
    """Test blocks."""
    chdir(os.path.join("fixtures", "blocks"))

    tackle_output = tackle(input)
    assert tackle_output == read_config_file(output)


ERROR_SOURCES = [
    ("empty-block-exception.yaml", EmptyBlockException),
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


def test_parser_list_to_block_macro(change_curdir_fixtures):
    os.chdir('macros')
    output = tackle('list-block.yaml')
    assert isinstance(output['foo'][1], list)


def test_parser_compact_hook_call_macro(change_curdir_fixtures):
    """Check that embedded compact hooks are called appropriately."""
    os.chdir('macros')
    output = tackle('compact-hook-macro.yaml')
    assert output['compact'] == 'things'


# def test_parser_compact_hook_call_macro(change_curdir_fixtures):
#     os.chdir('macros')
#     output = tackle('compact-hook-macro2.yaml')
#     assert output['compact'] == 'things'
