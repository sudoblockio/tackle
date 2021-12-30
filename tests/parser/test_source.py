"""Test the input source part of the parser."""
import pytest

from tackle.parser import update_source
from tackle.models import Context

INPUT_SOURCES = [
    # "github.com/robcxyz/tackle-demo"
    "robcxyz/tackle-demo"
]


@pytest.mark.parametrize("input_string", INPUT_SOURCES)
def test_parser_update_source(change_curdir_fixtures, input_string):
    """Test various inputs."""
    context = Context(input_string=input_string, no_input=True)
    update_source(context)


def test_parser_update_source_key_to_parent(chdir, mocker):
    """
    Test that when an input string is not a file/provider source that we correctly
    traverse to the nearest tackle file and run a key within it.
    """
    chdir('fixtures/input-key/child')
    context = Context(input_string="do_things", no_input=True)
    update_source(context)
    print()
