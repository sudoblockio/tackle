import pytest
import os
from ruamel.yaml import YAML

from tackle import tackle
from tackle.exceptions import FunctionCallException, HookParseException

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
    """
    Check that when no exec is given that by default the input is returned as is and
    validated.
    """
    output = tackle('field-types.yaml')

    # Based on validation of functions in fixture
    assert output


EXCEPTION_FIXTURES = [
    # Check that return string not found caught
    ('return-str-not-found.yaml', FunctionCallException),
    # Check that type checking works with no exec method.
    ('no-exec-type-error.yaml', HookParseException),
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
