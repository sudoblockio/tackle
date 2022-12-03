import pytest

from tackle import tackle
from tackle.cli import main
from tackle import exceptions


def test_parser_functions_exceptions_try_in_default(chdir):
    """
    When we have an error in a field's default like hook failure with `try`, we should
    catch that.
    """
    chdir('exceptions')
    with pytest.raises(exceptions.FunctionCallException):
        tackle('try-in-default.yaml')


def test_parser_functions_raises_unknown_arg(change_curdir_fixtures):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-default-hook-no-context.yaml", 'NOT_HERE')


def test_parser_functions_raises_unknown_kwarg(change_curdir_fixtures):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-default-hook-no-context.yaml", NOT_HERE='foo')


def test_parser_functions_raises_unknown_flags(change_curdir_fixtures):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-default-hook-no-context.yaml", global_flags=['NOT_HERE'])


def test_parser_functions_raises_unknown_arg_hook(change_curdir_fixtures):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-hook-no-context.yaml", 'run', 'NOT_HERE')


def test_parser_functions_raises_unknown_kwarg_hook(change_curdir_fixtures):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-hook-no-context.yaml", 'run', NOT_HERE='foo')


def test_parser_functions_raises_unknown_flags_hook(change_curdir_fixtures):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-hook-no-context.yaml", 'run', global_flags=['NOT_HERE'])


def test_parser_functions_raises_hook_kwarg_missing(chdir):
    chdir('exceptions')
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("hook-kwarg-missing.yaml", 'foo', baz='bang')


def test_parser_functions_raises_hook_kwarg_missing_default(chdir):
    chdir('exceptions')
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("hook-kwarg-missing-default.yaml", baz='bang')


def test_parser_functions_raises_validation_missing_field(chdir):
    chdir('exceptions')
    with pytest.raises(exceptions.MalformedFunctionFieldException):
        main(["missing-field.yaml", "stuff"])


def test_parser_functions_raises_(chdir):
    chdir('exceptions')
    with pytest.raises(exceptions.MalformedFunctionFieldException):
        main(["str-value.yaml", "stuff"])
