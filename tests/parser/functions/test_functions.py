import pytest
import os
from ruamel.yaml import YAML

from tackle import tackle
from tackle.exceptions import (
    FunctionCallException,
    HookParseException,
    MalformedFunctionFieldException,
)

FIXTURES = [
    ('call.yaml', 'call-output.yaml'),
    ('return.yaml', 'return-output.yaml'),
]


@pytest.mark.parametrize("fixture,expected_output", FIXTURES)
def test_function_model_extraction(change_curdir_fixtures, fixture, expected_output):
    yaml = YAML()
    with open(expected_output) as f:
        expected_output_dict = yaml.load(f)

    output = tackle(fixture)
    assert output == expected_output_dict


def test_function_no_exec(change_curdir_fixtures):
    """
    Check that when no exec is given that by default the input is returned as is and
    validated.
    """
    output = tackle('no-exec.yaml')

    assert output['no_arg_call']['target'] == 'world'
    assert output['arg_call']['target'] == 'things'


def test_function_field_types(change_curdir_fixtures):
    """Check that field types are respected."""
    output = tackle('field-types.yaml')
    # Based on validation of functions in fixture
    assert output


def test_function_extends(change_curdir_fixtures):
    """Check that we can extend a base function."""
    output = tackle('extends.yaml')
    assert output['t'] == ['hello', 'world']


def test_function_method(change_curdir_fixtures):
    """Check that methods work"""
    output = tackle('method-hook.yaml')
    assert output['t'] == {'in': 'foo', 'bar': 'baz'}
    assert output['t'] == output['jinja_method']
    assert output['jinja_base']['bar'] == 'foo'


def test_function_method_simple(change_curdir_fixtures):
    """Check that we can create a method."""
    output = tackle('method-single.yaml')
    assert output['do'] == {"v": ["Hello", "world!"]}


def test_function_method_embed(change_curdir_fixtures):
    """Check that we can create a method."""
    output = tackle('method-embed.yaml')
    assert output['do']['v'] == ['Hello', 'world!']


def test_function_method_inherit(change_curdir_fixtures):
    """Check that we can create a method."""
    output = tackle('method-inherit.yaml')
    assert output == {"t": "fooo"}


def test_function_method_args(change_curdir_fixtures):
    """Check that we can create a method that takes args."""
    output = tackle('method-args.yaml')
    assert output == {'foo': 'bar'}


def test_function_method_call_from_default(change_curdir_fixtures):
    """
    Check that we can create a method that takes args.
    See https://github.com/robcxyz/tackle/issues/99
    """
    output = tackle('method-call-from-default.yaml', target='foo')
    assert output['hi'] == 'Hello foo'


def test_function_method_maintain_context(change_curdir_fixtures):
    """Check a method that carries a context with it from the parent object."""
    output = tackle('method-maintain-context.yaml')
    assert output['do_greeter']['v'] == ['Hello', 'world!']
    assert output['jinja_call']['v'] == ['Hello', 'world!']


def test_function_method_nested(change_curdir_fixtures):
    """Check that we can create a method."""
    output = tackle('method-nested-hook.yaml')
    assert output['jinja_method_home']['destination'] == "earth"
    assert output['jinja_method_home'] == output['t_home']


def test_function_method_override(change_curdir_fixtures):
    """
    Check that when we call methods that attributes are properly overridden if they
     exist in the base.
    """
    output = tackle('method-nested-override.yaml')
    assert output['method_overlap_jinja']['home'] == 'earth'
    assert output['method_overlap_compact']['home'] == 'foo'
    assert output['attribute_override_jinja']['home'] == 'bing'
    assert output['attribute_override_compact']['home'] == 'bing'
    assert output['nested_jinja']['home'] == 'baz'
    assert output['nexted_compact']['home'] == 'baz'


def test_function_import_func_from_hooks_dir(change_curdir_fixtures):
    """Assert that we can call functions from local hooks dir."""
    os.chdir('func-provider')
    o = tackle()
    assert o['compact'] == 'a-default'
    assert o['jinja_extension_default'] == 'a-default'
    assert o['jinja_extension'] == 'things'
    # assert o['jinja_filter'] == 'things'


def test_function_import_func_from_hooks_dir_context_preserved(change_curdir_fixtures):
    """
    Check that when we run inside a nested dir, that a declarative hook carries context
    such as calling_directory.
    """
    os.chdir(os.path.join('func-provider-hook', 'a-dir'))
    o = tackle()
    assert o['compact'] == 'a-default'
    assert o['jinja_extension_default'] == 'a-default'
    assert o['jinja_extension'] == 'things'
    assert o['calling_dir'].endswith('a-dir')


def test_function_method_no_default(change_curdir_fixtures):
    """Assert that method calls with base fields with no default can be run."""
    o = tackle('method-call-no-default.yaml')
    assert o['compact']['v'] == 'foo'
    assert o['compact'] == o['expanded']
    assert o['jinja_base']['word'] == 'foo'
    assert o['jinja_method']['v'] == 'foo'


# Determine what lists do
# def test_function_list_call(change_curdir_fixtures):
#     """Check what compact hooks do."""
#     output = tackle('list-call.yaml')
#     assert output


# TODO: Build compact hook macro
# def test_function_compact(change_curdir_fixtures):
#     """Check what compact hooks do."""
#     output = tackle('compact.yaml')
#     assert output


def test_function_method_base_validate(change_curdir_fixtures):
    """Check that when a method uses a base attribute, that validation still happens."""
    with pytest.raises(Exception) as e:
        tackle('method-base-validate.yaml')
    assert 'string does not match regex' in e.value.message


EXCEPTION_FIXTURES = [
    # Check that return string not found caught
    ('return-str-not-found.yaml', FunctionCallException),
    # Check that type checking works with no exec method.
    ('no-exec-type-error.yaml', HookParseException),
    # Check args are required when they are not supplied.
    ('field-require.yaml', HookParseException),
    # Check that type is one of literals.
    ('field-bad-type.yaml', MalformedFunctionFieldException),
    # Check that type or default is given.
    ('field-type-or-default.yaml', MalformedFunctionFieldException),
]


@pytest.mark.parametrize("fixture,exception", EXCEPTION_FIXTURES)
def test_function_raises_exceptions(change_curdir_fixtures, fixture, exception):
    with pytest.raises(exception):
        tackle(fixture)


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
    with pytest.raises(HookParseException):
        tackle(f'field-types-{type_}-error-{field_input}.yaml')
