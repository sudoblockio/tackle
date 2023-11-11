import os
import pytest

from tackle.cli import main

COMMANDS = [
    (['input.yaml', 'bar', 'baz', '-pf', 'yaml'], 'foo: bar baz'),
]


@pytest.mark.parametrize("command,expected_output", COMMANDS)
def test_cli_commands(command, expected_output, capsys):
    """Assert output comes out of cli."""
    main(command)
    output = capsys.readouterr().out
    assert expected_output in output
