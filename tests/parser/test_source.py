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
    context = Context(input_string=input_string, no_input=True)
    update_source(context)
