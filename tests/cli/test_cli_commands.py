"""Collection of tests around tackle box's declarative command-line interface."""

import pytest
from tackle.cli import main

COMMANDS = [
    'tackle --help',
    # 'help --foo bar',
    # 'docs',
]


@pytest.fixture(params=COMMANDS)
def basic_commands(request):
    """Pytest fixture return both version invocation options."""
    return request.param


@pytest.mark.parametrize("command", COMMANDS)
def test_cli_commands(change_curdir_fixtures, command, capsys):
    """Asser output comes out of cli."""
    main(['tackle-hello.yaml'])
    assert 'Hello world!' in capsys.readouterr().out
