"""Collection of tests around tackle box's declarative command-line interface."""

import pytest


COMMANDS = [
    'tackle',
    # 'help --foo bar',
    # 'docs',
]


@pytest.fixture(params=COMMANDS)
def basic_commands(request):
    """Pytest fixture return both version invocation options."""
    return request.param


def test_cli_command(cli_runner, basic_commands):
    """Verify correct version output by `cookiecutter` on cli invocation."""
    result = cli_runner(basic_commands)
    print(result)
    # assert result.exit_code == 0
    # assert result.output.startswith('Tackle')
