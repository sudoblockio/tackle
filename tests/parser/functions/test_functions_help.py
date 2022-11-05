import pytest

from tackle import tackle


def test_function_default_hook_no_context_help(change_curdir_fixtures, capsys):
    """Validate that we can run a default hook's help."""
    with pytest.raises(SystemExit):
        tackle('cli-default-hook-no-context.yaml', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    with capsys.disabled():
        print(out)


def test_function_default_hook_no_context_method_call_help(
    change_curdir_fixtures, capsys
):
    """Validate that we can run a default hook's method help."""
    with pytest.raises(SystemExit):
        tackle('cli-default-hook-no-context.yaml', 'do', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    with capsys.disabled():
        print(out)


def test_function_cli_hook_arg_help(change_curdir_fixtures, capsys):
    """Validate that we can run a hook's with an arg."""
    with pytest.raises(SystemExit):
        tackle('cli-hook-no-context.yaml', 'run', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    with capsys.disabled():
        print(out)


def test_function_cli_hook_arg_help_no_arg(change_curdir_fixtures, capsys):
    """Validate that we can run a hook's with an arg."""
    with pytest.raises(SystemExit):
        tackle('cli-hook-no-context.yaml', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    with capsys.disabled():
        print(out)


def test_function_cli_no_default_hook(change_curdir_fixtures, capsys):
    """Check when there is no default hook we only display the available methods."""
    with pytest.raises(SystemExit):
        tackle('cli-no-default-hook.yaml', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    with capsys.disabled():
        print(out)
