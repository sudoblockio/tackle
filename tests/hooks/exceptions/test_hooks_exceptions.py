import os
import pytest

from tackle import tackle
from tackle.cli import main
from tackle import exceptions

EXCEPTION_FIXTURES = [
    # Check that return string not found caught
    ('return-str-not-found.yaml', exceptions.UnknownArgumentException),
    # # Check that type checking works with no exec method.
    # ('no-exec-type-error.yaml', exceptions.UnknownFieldInputException),
    # # Check args are required when they are not supplied.
    # ('field-require.yaml', exceptions.HookParseException),
    # # Check that type is one of literals.
    # # TODO: This error will change with composition
    # ('field-bad-type.yaml', exceptions.MalformedFunctionFieldException),
    # # Check when extends is used with a missing base.
    # ('extends-missing.yaml', exceptions.MalformedFunctionFieldException),
    # # Check when extends is a dict an error is thrown
    # ('extends-dict.yaml', exceptions.MalformedFunctionFieldException),
]


@pytest.mark.parametrize("fixture,exception", EXCEPTION_FIXTURES)
def test_hooks_raises_exceptions(fixture, exception):
    with pytest.raises(exception):
        tackle(fixture)


def test_hooks_method_base_validate():
    """Check that when a method uses a base attribute, that validation still happens."""
    # TODO: Fix me with methods
    # with pytest.raises(exceptions.UnknownInputArgumentException) as e:
    tackle('method-base-validate.yaml')
    # TODO: pyd 2 update - pattern  to regex
    # assert 'string does not match regex' in e.value.message


def test_hooks_exceptions_try_in_default():
    """
    When we have an error in a field's default like hook failure with `try`, we should
     catch that.
    """
    # TODO: Issue with this is that if we have a string flag we don't know how to
    #  perform a macro on it and the output is extremely confusing
    # with pytest.raises(exceptions.FunctionCallException):
    #     tackle('try-in-default.yaml')
    output = tackle('try-in-default.yaml')
    pass


def test_parser_functions_raises_unknown_arg():
    """When we have a default hook we should raise an error if the arg is not there."""
    with pytest.raises(exceptions.UnknownInputArgumentException) as e:
        tackle("hook-default-arg-missing.yaml", 'NOT_HERE')

    assert "default hook" in e.value.message


def test_parser_functions_raises_unknown_kwarg(chdir):
    """Same as above but with kwarg"""
    with pytest.raises(exceptions.MalformedHookFieldException) as e:
        tackle("hook-default-arg-missing.yaml", NOT_HERE='foo')

    assert "default hook" in e.value.message


def test_parser_functions_raises_unknown_flags(chdir):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-default-hook-no-context.yaml", global_flags=['NOT_HERE'])


def test_parser_functions_raises_unknown_arg_hook(chdir):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-hook-no-context.yaml", 'run', 'NOT_HERE')


def test_parser_functions_raises_unknown_kwarg_hook(chdir):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("cli-hook-no-context.yaml", "run", NOT_HERE='foo')


def test_parser_functions_raises_unknown_flags_hook(chdir):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        # tackle("cli-hook-no-context.yaml", "run", not_here=True)
        tackle("cli-hook-no-context.yaml", "run", **{'NOT_HERE': True})


def test_parser_functions_raises_hook_kwarg_missing(chdir):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("hook-kwarg-missing.yaml", 'foo', baz='bang')


def test_parser_functions_raises_hook_kwarg_missing_default(chdir):
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("hook-kwarg-missing-default.yaml", baz='bang')


def test_parser_functions_raises_validation_missing_field(chdir):
    with pytest.raises(exceptions.MalformedHookFieldException):
        main(["missing-field.yaml", "stuff"])


def test_parser_functions_raises_(chdir):
    with pytest.raises(exceptions.MalformedHookFieldException):
        main(["str-value.yaml", "stuff"])
