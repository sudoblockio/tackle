"""Collection of tests around tackle box's declarative command-line interface."""

import pytest
from tackle.cli import main

COMMANDS = [
    (['global-kwarg.yaml', '--key_a', '"stuff and things"'], 'stuff and things'),
]


@pytest.mark.parametrize("command,expected_output", COMMANDS)
def test_cli_commands(change_curdir_fixtures, command, expected_output, capsys):
    """Asser output comes out of cli."""
    main(command)
    assert expected_output in capsys.readouterr().out
