import pytest

from tackle.cli import main


def test_cli_parse_args_help_arg_base(change_curdir_fixtures, capsys):
    with pytest.raises(SystemExit):
        main(["help.yaml", "help"])
    out, err = capsys.readouterr()
    assert out == "Foo\n"
    print(out, err)


def test_cli_parse_args_help_arg_for_func(change_curdir_fixtures, capsys):
    with pytest.raises(SystemExit):
        main(["help.yaml", "with_help", "help"])
    out, err = capsys.readouterr()
    assert out == "Foo\n"
    print(out, err)


def test_cli_parse_args_help_arg_for_func_with_method(change_curdir_fixtures, capsys):
    with pytest.raises(SystemExit):
        main(["help.yaml", "with_help_methods", "help"])
    out, err = capsys.readouterr()
    assert out == "Foo\n"
    print(out, err)


def test_cli_parse_args_help_arg_base_remote(change_curdir_fixtures, capsys):
    with pytest.raises(SystemExit):
        main(["robcxyz/tackle-hello-world", "help"])
    out, err = capsys.readouterr()
    assert out == "Foo\n"
    print(out, err)


def test_cli_parse_args_help_arg_for_func_remote(change_curdir_fixtures, capsys):
    with pytest.raises(SystemExit):
        main(["robcxyz/tackle-hello-world", "with_help", "help"])
    out, err = capsys.readouterr()
    assert out == "Foo\n"
    print(out, err)
