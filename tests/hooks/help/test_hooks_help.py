import os

import pytest

from tackle import tackle


@pytest.mark.parametrize(
    "file,args",
    [
        ('all-types.yaml', ['help']),
        ('all-types.yaml', ['MyHook', 'help']),
        ('default-hook.yaml', ['help']),
        ('base-hook.yaml', ['MyHook', 'help']),
        ('method.yaml', ['MyHook', 'MyMethod', 'help']),
    ],
)
def test_hooks_help_parameterized(capsys, file, args):
    with pytest.raises(SystemExit):
        tackle(file, *args)
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    assert "Some things that do stuff" in out
    assert "flags:" in out
    assert "options:" in out
    assert "methods:" in out


def test_hooks_help_no_hook_arg(capsys):
    with pytest.raises(SystemExit):
        tackle('base-hook.yaml', 'help')
    out, err = capsys.readouterr()

    assert "usage: tackle" in out
    assert "MyHook" in out
    assert "A CLI thing" in out


def test_hooks_help_type_complex(capsys):
    with pytest.raises(SystemExit):
        tackle('types-complex.yaml', 'help')
    out, err = capsys.readouterr()

    assert "usage: tackle" in out
    assert "[IPv4Address]" in out
    assert "[Union[str, int]]" in out
    assert "[BaseHook]" in out


def test_hooks_help_python_provider(capsys):
    with pytest.raises(SystemExit):
        tackle('python-provider', 'help')
    out, err = capsys.readouterr()

    assert "usage: tackle" in out
    assert "an_optional_str" in out
    assert "str_required" in out
    assert "str_desc" in out
    assert "python_types" in out
    assert "A python hook" in out


# def test_hooks_extends_visible(cd_fixtures, capsys):
#     """Check when there is no default hook we only display the available methods."""
#     with pytest.raises(SystemExit):
#         tackle('cli-no-default-hook.yaml', 'help')
#     out, err = capsys.readouterr()
#     assert "usage: tackle" in out


def test_hooks_cli_tackle_help_with_arg(cd):
    """
    Check that when we are in a dir with a default tackle file, we can get help when
     calling a declarative hook.
    """
    cd(os.path.join('../fixtures', 'a-tackle'))
    with pytest.raises(SystemExit):
        tackle('stuff', 'help')


def test_hooks_help_default_hook_embedded(capsys):
    """Check when getting help with a method that it works."""
    with pytest.raises(SystemExit):
        tackle('default-hook-embedded.yaml', 'run', 'do', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    assert "stuff" in out
    assert "bar" in out
    assert "normal_hook" in out


def test_hooks_help_default_hook_embedded_default(capsys):
    """Check when getting help with a method in a default hook that it works."""
    with pytest.raises(SystemExit):
        tackle('default-hook-embedded.yaml', 'do', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    assert "stuff" in out
    assert "bar" in out
    assert "default_hook" in out


def test_hooks_import_func_from_hooks_dir_method_no_help(capsys):
    """
    Check that when there is no help in the hook / method that we still show help
     screen with minmal info.
    """
    with pytest.raises(SystemExit):
        tackle('minimal.yaml', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    assert "methods:" in out
    assert "MyHook" in out


# def test_hooks_cli_tackle_arg_error(chdir):
#     """Check that when we give a bad key, even with help we get an exception."""
#     chdir(os.path.join('../fixtures', 'a-tackle'))
#     with pytest.raises(exceptions.UnknownInputArgumentException):
#         tackle('bad-key', 'help')
