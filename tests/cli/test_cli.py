"""Test the cli."""
import pytest
import os

from tackle.models import Context
from tackle.cli import main

# fmt: off
INPUT_SOURCES = [
    ("github.com/robcxyz/tackle-demo", {'input_string': "github.com/robcxyz/tackle-demo"}),
    ("robcxyz/tackle-demo --no-input", {'input_string': 'robcxyz/tackle-demo', 'no_input': True}),
    ("thing --no-input", {'input_string': 'thing', 'no_input': True}),
    ("thing --foo bar", {'input_string': 'thing'}),
]
# fmt: on


@pytest.mark.parametrize("input_string,output", INPUT_SOURCES)
def test_cli_parse_args(mocker, change_dir_base, input_string, output):
    """Mock the main call and verify the args get passed in right through the CLI."""
    mock = mocker.patch("tackle.main.update_source", autospec=True, return_value={})
    main(input_string.split(' '))

    assert mock.called
    assert isinstance(mock.call_args[0][0], Context)

    context = mock.call_args[0][0].dict()

    for k, v in output.items():
        assert k in context
        assert context[k] == v


def test_cli_parse_args_empty(mocker, change_dir_base):
    """When no arg is given we should find the closest tackle file."""
    mock = mocker.patch("tackle.main.update_source", autospec=True, return_value={})
    main([])

    assert mock.called
    assert isinstance(mock.call_args[0][0], Context)
    context = mock.call_args[0][0].dict()
    assert context['input_string'] == os.path.abspath('.tackle.yaml')
