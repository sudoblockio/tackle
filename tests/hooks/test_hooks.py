import pytest

from tackle import tackle
from tackle.factory import new_context
from tackle.hooks import create_dcl_hook, create_default_factory


@pytest.mark.parametrize(
    "file", ['field-types.yaml', 'field-types-default.yaml', 'field-types-type.yaml']
)
def test_hooks_field_types(cd_fixtures, file):
    """Check that field types are respected."""
    output = tackle(file)

    assert output['call']['a_str'] == 'foo'
    assert output['call']['a_bool']
    assert output['call']['a_int'] == 1
    assert output['call']['a_float'] == 1.2
    assert output['call']['a_list'] == ['stuff', 'things']
    assert output['call']['a_dict'] == {'stuff': 'things'}


def test_hooks_supplied_kwargs_param_dict(cd_fixtures):
    """
    Test that we can populate a functions fields with a `kwargs` key as a dict that is
     a dict that will update the field's values.
    """
    output = tackle('supplied-kwargs-param-dict.yaml')
    assert output['call']['bar'] == 'bing'


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


def test_create_default_factory_walker():
    value = {
        'default_factory': {
            'in': {'->': 'literal bar'},
            'out': {'->': 'return in'},
        }
    }
    create_default_factory(context=new_context(), hook_name='', value=value)
    output = value['default_factory']()  # noqa

    assert output == 'bar'


DCL_HOOK_FIXTURES: list[dict] = [
    {'stuff': 'things'},
    {
        'stuff': {
            'default': 'things',
        }
    },
    {
        'stuff': {
            'type': 'str',
            'default': 'things',
        },
    },
    {
        'stuff': {
            'enum': ['foo', 'things'],
            'default': 'things',
        },
    },
    {
        'stuff->': 'literal things',
    },
    {
        'stuff': {
            '->': 'literal things',
        }
    },
    {
        'stuff': {
            '->': 'literal things',
            'if': True,
        }
    },
]


@pytest.mark.parametrize("hook_input_raw", DCL_HOOK_FIXTURES)
def test_hooks_create_dcl_hook_simple_params(context, hook_input_raw):
    Hook = create_dcl_hook(
        context=context, hook_name="foo", hook_input_raw=hook_input_raw
    )
    hook = Hook()
    assert hook.hook_name == 'foo'
    assert hook.stuff == 'things'


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
