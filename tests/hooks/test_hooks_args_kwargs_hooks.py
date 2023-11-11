import pytest
import os
from ruyaml import YAML

from tackle import tackle

FIXTURES = [
    ('call.yaml', 'call-output.yaml'),
    ('return.yaml', 'return-output.yaml'),
    ('return-render.yaml', 'return-output.yaml'),
]


@pytest.mark.parametrize("fixture,expected_output", FIXTURES)
def test_hooks_model_extraction(cd_fixtures, fixture, expected_output):
    yaml = YAML()
    with open(expected_output) as f:
        expected_output_dict = yaml.load(f)

    output = tackle(fixture)
    assert output == expected_output_dict


def test_hooks_no_exec(cd_fixtures):
    """
    Check that when no exec is given that by default the input is returned as is and
    validated.
    """
    output = tackle('no-exec.yaml')

    assert output['no_arg_call']['target'] == 'world'
    assert output['arg_call']['target'] == 'things'


@pytest.mark.parametrize("file", [
    'field-types.yaml',
    'field-types-default.yaml',
    'field-types-type.yaml'
])
def test_hooks_field_types(cd_fixtures, file):
    """Check that field types are respected."""
    output = tackle(file)
    assert output['call']['a_str'] == 'foo'
    assert output['call']['a_bool'] == True
    assert output['call']['a_int'] == 1
    assert output['call']['a_float'] == 1.2
    assert output['call']['a_list'] == ['stuff', 'things']
    assert output['call']['a_dict'] == {'stuff': 'things'}


def test_hooks_merge_field_into_hook(cd_fixtures):
    """Verify that we can merge a dict into the parent's field."""
    os.chdir('functions')
    o = tackle('merge-field.yaml', 'foo')
    assert o


def test_hooks_method_no_default(chdir):
    """Assert that method calls with base fields with no default can be run."""
    chdir('method-fixtures')
    o = tackle('method-call-no-default.yaml')
    assert o['compact']['v'] == 'foo'
    assert o['compact'] == o['expanded']
    assert o['jinja_base']['word'] == 'foo'
    assert o['jinja_method']['v'] == 'foo'


def test_hooks_supplied_kwargs_param_dict(cd_fixtures):
    """
    Test that we can populate a functions fields with a `kwargs` key as a dict that is
     a dict that will update the field's values.
    """
    output = tackle('supplied-kwargs-param-dict.yaml')
    assert output['kwarg']['bar'] == 'bing'
    assert output['kwarg'] == output['call']


def test_hooks_supplied_kwargs_param_str(cd_fixtures):
    """
    Test that we can populate a functions fields with a `kwargs` key as a str that is
     a dict that will update the field's values.
    """
    output = tackle('supplied-kwargs-param-str.yaml')
    assert output['kwarg']['bar'] == 'bing'
    assert output['kwarg'] == output['call']


def test_hooks_supplied_kwargs_param_str_loop(cd_fixtures):
    """Check that we can use kwargs within a loop"""
    output = tackle('supplied-kwargs-param-str-loop.yaml')
    assert output['call'][0]['bar'] == 'bing'
    assert len(output['call']) == 2


def test_hooks_supplied_args_param_str(cd_fixtures):
    """Test that we can populate a functions args with an `args` key as str."""
    output = tackle('supplied-args-param-str.yaml')
    assert output['call']['bar'] == 'bing'


def test_hooks_supplied_args_param_list(cd_fixtures):
    """Test that we can populate a functions args with an `args` key as list."""
    output = tackle('supplied-args-param-list.yaml')
    assert output['call']['bar'] == 'bing bling'

# Determine what lists do
# def test_hooks_list_call(cd_fixtures):
#     """Check what compact hooks do."""
#     output = tackle('list-call.yaml')
#     assert output


# TODO: Build compact hook macro
# def test_hooks_compact(cd_fixtures):
#     """Check what compact hooks do."""
#     output = tackle('compact.yaml')
#     assert output
