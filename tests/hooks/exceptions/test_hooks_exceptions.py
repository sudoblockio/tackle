import pytest

from tackle import exceptions, tackle
from tackle.cli import main

EXCEPTION_FIXTURES = [
    # Check that type checking works with no exec method.
    ('no-exec-type-error.yaml', exceptions.HookParseException),
    # Check args are required when they are not supplied.
    ('field-require.yaml', exceptions.HookParseException),
    # Check that type is one of literals.
    ('field-bad-type.yaml', exceptions.MalformedHookFieldException),
    # Check when extends is used with a missing base.
    ('extends-missing.yaml', exceptions.MalformedHookFieldException),
    # Check when extends is a dict an error is thrown
    ('extends-dict.yaml', exceptions.HookParseException),
    # Check that when a hook is unknown we raise a error
    ('unknown-hook.yaml', exceptions.UnknownHookTypeException),
    # # Check that when a method is unknown we raise a error
    ('unknown-method.yaml', exceptions.UnknownHookTypeException),
]


@pytest.mark.parametrize("fixture,exception", EXCEPTION_FIXTURES)
def test_hooks_raises_exceptions(fixture, exception):
    with pytest.raises(exception):
        tackle(fixture)


def test_hooks_method_base_validate():
    """Check that when a method uses a base attribute, that validation still happens."""
    with pytest.raises(exceptions.HookParseException) as e:
        tackle('method-base-validate.yaml')
    assert 'String should match pattern' in e.value.message


def test_hooks_exceptions_try_in_default():
    """
    When we have an error in a field's default like hook failure with `try`, we should
     catch that.
    """
    # TODO: This is the wrong error and appears since the macro expands the field hook
    #  call and tries to render the output. This can be improved since the try / if
    #  should be caught sooner.
    with pytest.raises(exceptions.UnknownTemplateVariableException):
        tackle('try-in-default.yaml')


def test_hooks_exceptions_raises_unknown_arg():
    """When we have a default hook we should raise an error if the arg is not there."""
    with pytest.raises(exceptions.UnknownHookInputArgumentException) as e:
        tackle("hook-default-arg-missing.yaml", 'NOT_HERE')

    assert "The input_arg=" in e.value.message.__str__()


def test_hooks_exceptions_raises_unknown_kwarg():
    """Same as above but with kwarg"""
    with pytest.raises(exceptions.UnknownHookInputArgumentException) as e:
        tackle("hook-default-arg-missing.yaml", NOT_HERE='foo')

    assert "NOT_HERE" in e.value.message.__str__()


def test_hooks_exceptions_raises_unknown_flags():
    with pytest.raises(exceptions.UnknownHookInputArgumentException):
        tackle("no-args.yaml", NOT_HERE=True)


def test_hooks_exceptions_raises_unknown_arg_hook():
    with pytest.raises(exceptions.UnknownHookInputArgumentException):
        tackle("no-args.yaml", 'run', 'NOT_HERE')


def test_hooks_exceptions_raises_unknown_kwarg_hook():
    with pytest.raises(exceptions.UnknownHookInputArgumentException):
        tackle("no-args.yaml", "run", NOT_HERE='foo')


def test_hooks_exceptions_raises_unknown_flags_hook():
    with pytest.raises(exceptions.UnknownHookInputArgumentException):
        tackle("no-args.yaml", "run", **{'NOT_HERE': True})


def test_hooks_exceptions_raises_hook_kwarg_missing():
    with pytest.raises(exceptions.UnknownHookInputArgumentException):
        tackle("hook-kwarg-missing.yaml", 'foo', baz='bang')


def test_hooks_exceptions_raises_hook_kwarg_missing_default():
    with pytest.raises(exceptions.UnknownHookInputArgumentException):
        tackle("hook-kwarg-missing-default.yaml", baz='bang')


def test_hooks_exceptions_raises_validation_missing_field():
    with pytest.raises(exceptions.MalformedHookFieldException):
        main(["missing-field.yaml", "stuff"])


def test_hooks_exceptions_raises_on_str_hook_value():
    """When a hook's value is a string type."""
    with pytest.raises(exceptions.MalformedHookDefinitionException):
        main(["str-value.yaml", "stuff"])


def test_hooks_exceptions_raises_on_list_hook_value():
    """When a hook's value is a list type."""
    with pytest.raises(exceptions.MalformedHookDefinitionException):
        main(["list-value.yaml", "stuff"])


# TODO: Appears that python hooks are not validating properly
#  https://github.com/sudoblockio/tackle/issues/223
def test_hooks_exceptions_raises_on_dict_hook_value(cd):
    """When a hook's base field is not the right type - args: dict in this case."""
    cd('bad-hooks')
    with pytest.raises(exceptions.MalformedHookDefinitionException):
        o = tackle('hook_1')
        # assert o
