import os
import pytest

from tackle import tackle
from tackle import exceptions


def test_function_default_hook_no_context_help(change_curdir_fixtures, capsys):
    """Validate that we can run a default hook's help."""
    with pytest.raises(SystemExit):
        tackle('cli-default-hook-no-context.yaml', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    # with capsys.disabled():
    #     print(out)


def test_function_default_hook_no_context_method_call_help(chdir, capsys):
    """Validate that we can run a hook method's help with visible field."""
    chdir('field-hooks-fixtures')
    with pytest.raises(SystemExit):
        tackle('extends-visible.yaml', 'foo', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    assert "network_info" not in out


def test_function_cli_hook_arg_help(change_curdir_fixtures, capsys):
    """Validate that we can run a hook's with an arg."""
    with pytest.raises(SystemExit):
        tackle('cli-hook-no-context.yaml', 'run', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    # with capsys.disabled():
    #     print(out)


def test_function_cli_hook_arg_help_no_arg(change_curdir_fixtures, capsys):
    """Validate that we can run a hook's with an arg."""
    with pytest.raises(SystemExit):
        tackle('cli-hook-no-context.yaml', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    assert 'foo' not in out  # Taken out with `visible:False` field
    # with capsys.disabled():
    #     print(out)


def test_function_cli_no_default_hook(change_curdir_fixtures, capsys):
    """Check when there is no default hook we only display the available methods."""
    with pytest.raises(SystemExit):
        tackle('cli-no-default-hook.yaml', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    # with capsys.disabled():
    #     print(out)


def test_function_cli_default_hook_embedded(change_curdir_fixtures, capsys):
    """Check when getting help with a method that it works."""
    with pytest.raises(SystemExit):
        tackle('cli-default-hook-embedded.yaml', 'run', 'do', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    # with capsys.disabled():
    #     print(out)


# def test_function_extends_visible(change_curdir_fixtures, capsys):
#     """Check when there is no default hook we only display the available methods."""
#     with pytest.raises(SystemExit):
#         tackle('cli-no-default-hook.yaml', 'help')
#     out, err = capsys.readouterr()
#     assert "usage: tackle" in out


def test_function_cli_tackle_help_no_arg(chdir):
    """Check that when we are in a dir with a default tackle file, we can get help."""
    chdir(os.path.join('fixtures', 'a-tackle'))
    with pytest.raises(SystemExit):
        tackle('help')


def test_function_cli_tackle_default_unknown(change_curdir_fixtures, capsys):
    """
    Check that when the type is not provided because there is some hook for the
     default is unknown.
    """
    with pytest.raises(SystemExit):
        tackle('cli-hook-type-unknown.yaml', 'help')
    out, _ = capsys.readouterr()
    assert "[unknown]" in out


def test_function_cli_tackle_help_with_arg(chdir):
    """
    Check that when we are in a dir with a default tackle file, we can get help when
     calling a declarative hook.
    """
    chdir(os.path.join('fixtures', 'a-tackle'))
    with pytest.raises(SystemExit):
        tackle('stuff', 'help')


def test_function_cli_tackle_arg_error(chdir):
    """Check that when we give a bad key, even with help we get an exception."""
    chdir(os.path.join('fixtures', 'a-tackle'))
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle('bad-key', 'help')
