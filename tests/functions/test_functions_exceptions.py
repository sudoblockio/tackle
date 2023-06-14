import os
import pytest

from tackle import tackle
from tackle.cli import main
from tackle import exceptions

EXCEPTION_FIXTURES = [
    # Check that return string not found caught
    ('return-str-not-found.yaml', exceptions.FunctionCallException),
    # Check that type checking works with no exec method.
    ('no-exec-type-error.yaml', exceptions.HookParseException),
    # Check args are required when they are not supplied.
    ('field-require.yaml', exceptions.HookParseException),
    # Check that type is one of literals.
    ('field-bad-type.yaml', exceptions.MalformedFunctionFieldException),
    # Check when extends is used with a missing base.
    ('extends-missing.yaml', exceptions.MalformedFunctionFieldException),
    # Check when extends is a dict an error is thrown
    ('extends-dict.yaml', exceptions.MalformedFunctionFieldException),
]


@pytest.mark.parametrize("fixture,exception", EXCEPTION_FIXTURES)
def test_function_raises_exceptions(chdir, fixture, exception):
    chdir('exceptions')
    with pytest.raises(exception):
        tackle(fixture)


def test_function_method_base_validate(chdir):
    """Check that when a method uses a base attribute, that validation still happens."""
    chdir('method-fixtures')
    with pytest.raises(Exception) as e:
        tackle('method-base-validate.yaml')
    assert 'string does not match regex' in e.value.message


FIELD_TYPE_EXCEPTION_FIXTURES = [
    ('str', 'str'),
    ('dict', 'str'),
    ('list', 'str'),
    ('str', 'type'),
    ('dict', 'type'),
    ('list', 'type'),
    ('str', 'default'),
    ('dict', 'default'),
    ('list', 'default'),
]


@pytest.mark.parametrize("type_,field_input", FIELD_TYPE_EXCEPTION_FIXTURES)
def test_function_raises_exceptions_field_types(chdir, type_, field_input):
    """Check that a validation error is returned for each type of field definition."""
    chdir(os.path.join('fixtures', 'field-type-exceptions'))
    with pytest.raises(exceptions.HookParseException):
        tackle(f'field-types-{type_}-error-{field_input}.yaml')


def test_parser_functions_exceptions_try_in_default(chdir):
    """
    When we have an error in a field's default like hook failure with `try`, we should
    catch that.
    """
    chdir('exceptions')
    with pytest.raises(exceptions.FunctionCallException):
        tackle('try-in-default.yaml')


def test_parser_functions_raises_unknown_arg(chdir):
    chdir('cli-fixtures')
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-default-hook-no-context.yaml", 'NOT_HERE')


def test_parser_functions_raises_unknown_kwarg(chdir):
    chdir('cli-fixtures')
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-default-hook-no-context.yaml", NOT_HERE='foo')


def test_parser_functions_raises_unknown_flags(chdir):
    chdir('cli-fixtures')
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-default-hook-no-context.yaml", global_flags=['NOT_HERE'])


def test_parser_functions_raises_unknown_arg_hook(chdir):
    chdir('cli-fixtures')
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-hook-no-context.yaml", 'run', 'NOT_HERE')


def test_parser_functions_raises_unknown_kwarg_hook(chdir):
    chdir('cli-fixtures')
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-hook-no-context.yaml", 'run', NOT_HERE='foo')


def test_parser_functions_raises_unknown_flags_hook(chdir):
    chdir('cli-fixtures')
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
