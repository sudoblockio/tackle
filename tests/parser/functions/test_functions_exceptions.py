import pytest

from tackle import tackle
from tackle import exceptions


def test_parser_functions_raises_unknown_arg(change_curdir_fixtures):
    with pytest.raises(exceptions.UnknownArgumentException):
        tackle("cli-default-hook-no-context.yaml", 'NOT_HERE')


def test_parser_functions_raises_unknown_kwarg(change_curdir_fixtures):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-default-hook-no-context.yaml", NOT_HERE='foo')


def test_parser_functions_raises_unknown_flags(change_curdir_fixtures):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-default-hook-no-context.yaml", global_flags=['NOT_HERE'])


def test_parser_functions_raises_unknown_arg_hook(change_curdir_fixtures):
    with pytest.raises(exceptions.UnknownArgumentException):
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
