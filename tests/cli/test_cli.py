"""Test the cli."""
import pytest
import os

from tackle.context import Context
from tackle.cli import main

# fmt: off
INPUT_SOURCES = [
    (
        "thing --foo",
        {'args': ['thing'], 'kwargs': {'foo': True}},
    ),
    (
        "thing --foo bar",
        {'args': ['thing'], 'kwargs': {'foo': 'bar'}},
    ),
    (
        "thing --foo=bar",
        {'args': ['thing'], 'kwargs': {'foo': 'bar'}}
    ),
    (
        "thing --foo1=bar --foo2=bar",
        {'args': ['thing'], 'kwargs': {'foo1': 'bar', 'foo2': 'bar'}}
    ),
    (
        "thing foo bar",
        {'args': ['thing', 'foo', 'bar'], 'kwargs': {}},
    ),
]
# fmt: on


@pytest.mark.parametrize("input_string,output", INPUT_SOURCES)
def test_cli_parse_args(mocker, change_base_dir, input_string, output):
    """Mock the main call and verify the args get passed in right through the CLI."""
    mock = mocker.patch("tackle.main.parse_context", autospec=True)
    main(input_string.split(' '))

    context = mock.call_args[0][0]

    assert mock.called
    assert isinstance(context, Context)
    for k, v in output.items():
        assert getattr(context.input, k) == v


def test_cli_parse_args_empty(mocker):
    """When no arg is given we should find the closest tackle file."""
    mock = mocker.patch("tackle.main.parse_context", autospec=True)
    main([])
    assert mock.called
    assert isinstance(mock.call_args[0][0], Context)

    context = mock.call_args[0][0]
    assert context.source.file == os.path.abspath('.tackle.yaml')



@pytest.mark.parametrize("input_string", ["--print", "-p"])
def test_cli_parse_args_print_option(mocker, capsys, input_string):
    """When no arg is given we should find the closest tackle file."""
    mocker_main = mocker.patch("tackle.main.parse_context", autospec=True)
    mocker_cli = mocker.patch("tackle.cli.print_public_data", autospec=True)
    main([input_string])
    assert mocker_main.called
    assert mocker_cli.called


def test_cli_parse_args_help():
    """Test help arg."""
    with pytest.raises(SystemExit) as e:
        main(["--help"])
        assert e.value.code == 0

    with pytest.raises(SystemExit) as e:
        main(["-h"])
        assert e.value.code == 0


def test_cli_parse_args_version():
    """Test version arg."""
    with pytest.raises(SystemExit) as e:
        main(["--version"])
        assert e.value.code == 0
