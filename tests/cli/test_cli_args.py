import pytest
from tackle.cli import main

COMMANDS = [
    (['global-kwarg.yaml', '--key_a', '"stuff and things"'], 'stuff and things'),
    (['input.yaml', 'bar', 'baz', '-pf', 'yaml'], 'foo: bar baz'),
]


@pytest.mark.parametrize("command,expected_output", COMMANDS)
def test_cli_commands(change_curdir_fixtures, command, expected_output, capsys):
    """Assert output comes out of cli."""
    main(command)
    output = capsys.readouterr().out
    assert expected_output in output


def test_cli_command_find_in_parent(chdir_fixture, capsys):
    """Check that we can change into a child dir and find a file in parent with flag."""
    chdir_fixture('dir')
    main(['global-kwarg.yaml', '--key_a', '"stuff and things"', '--find-in-parent'])
    assert 'stuff and things' in capsys.readouterr().out
