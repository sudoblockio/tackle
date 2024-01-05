import os
import sys

import pytest

from tackle.cli import main
from tackle.context import Context

INPUT_SOURCES = [
    (
        "thing --foo",
        {'args': ['thing'], 'kwargs': {'foo': True}},
    ),
    (
        "thing --foo bar",
        {'args': ['thing'], 'kwargs': {'foo': 'bar'}},
    ),
    ("thing --foo=bar", {'args': ['thing'], 'kwargs': {'foo': 'bar'}}),
    (
        "thing --foo1=bar --foo2=bar",
        {'args': ['thing'], 'kwargs': {'foo1': 'bar', 'foo2': 'bar'}},
    ),
    (
        "thing foo bar",
        {'args': ['thing', 'foo', 'bar'], 'kwargs': {}},
    ),
    (
        "--helpo --world",
        {'args': [], 'kwargs': {'helpo': True, 'world': True}},
    ),
    (
        "--thing=foo",
        {'args': [], 'kwargs': {'thing': 'foo'}},
    ),
    (
        "--thing=foo --stuff",
        {'args': [], 'kwargs': {'thing': 'foo', 'stuff': True}},
    ),
    (
        "--thing foo",
        {'args': [], 'kwargs': {'thing': 'foo'}},
    ),
    (
        "--thing foo --stuff foo",
        {'args': [], 'kwargs': {'thing': 'foo', 'stuff': 'foo'}},
    ),
    (
        "--thing foo --stuff",
        {'args': [], 'kwargs': {'thing': 'foo', 'stuff': True}},
    ),
    (
        "--thing foo bar",
        {'args': [], 'kwargs': {'thing': 'foo bar'}},
    ),
    (
        "--thing 1",
        {'args': [], 'kwargs': {'thing': 1}},
    ),
    (
        "--thing true",
        {'args': [], 'kwargs': {'thing': True}},
    ),
    # Does not work because quotes are eaten by argparse and bar becomes an arg
    # (
    #     "--thing='foo bar'",
    #     {'args': [], 'kwargs': {'thing': 'foo bar'}},
    # ),
]


@pytest.mark.parametrize("input_string,output", INPUT_SOURCES)
def test_cli_parse_args(mocker, cd_base_dir, input_string, output):
    """Mock the main call and verify the args get passed in right through the CLI."""
    mock = mocker.patch("tackle.main.parse_context", autospec=True)
    main(input_string.split(' '))

    context = mock.call_args[0][0]

    assert mock.called
    assert isinstance(context, Context)
    for k, v in output.items():
        assert getattr(context.input, k) == v


@pytest.mark.parametrize(
    "input_string,output_keys,output",
    [
        ("--latest", "latest", True),
        ("--file foo", "file", "foo"),
        ("--directory foo", "directory", "foo"),
        ("--find-in-parent", "find_in_parent", True),
    ],
)
def test_cli_parse_args_vars(mocker, cd_base_dir, input_string, output_keys, output):
    """Mock the main call and verify the args get passed in right through the CLI."""
    mock = mocker.patch("tackle.cli.tackle", autospec=True)
    main(input_string.split(' '))

    assert mock.called
    assert mock.call_args.kwargs[output_keys] == output


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


def test_cli_call_mock(mocker):
    """Check the main function runs properly."""
    mock = mocker.patch("tackle.main.parse_context")
    main("stuff")

    assert mock.called


def test_cli_coerce_types(mocker):
    """When the input is a native type, use that instead of just strings."""
    mock = mocker.patch("tackle.cli.tackle")
    main(['1', '1.2', 'true'])

    assert mock.called
    assert mock.call_args.args == (1, 1.2, True)


def test_cli_call_empty(mocker):
    """
    Check that when no arg is given that we find the closest tackle file which
     could be in the parent directory.
    """
    mock = mocker.patch("tackle.main.parse_context")
    main([])

    assert mock.called
    local_tackle = os.path.join(os.path.abspath('.'), '.tackle.yaml')

    if sys.version_info.minor > 7:
        assert mock.call_args.args[0].path.calling.file == local_tackle
    # test was failing in 3.7/6
    else:
        assert mock.call_args[0][0].path.calling.file == local_tackle


COMMANDS = [
    (['tackle-hello.yaml'], 'Hello world!'),
    (['input-arg.yaml', 'bar', 'baz', '-pf', 'yaml'], 'foo: bar baz'),
    (['input-args.yaml', 'baz', '1', '-pf', 'yaml'], 'bar: 1'),
    (['input-args.yaml', 'baz', '1', '-pf', 'json'], '"bar": 1}'),
]


@pytest.mark.parametrize("command,expected_output", COMMANDS)
def test_cli_commands(command, expected_output, capsys):
    """Asser output comes out of cli."""
    main(command)
    output = capsys.readouterr().out
    assert expected_output in output
