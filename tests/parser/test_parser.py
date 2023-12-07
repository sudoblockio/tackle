import pytest

from tackle.parser import get_for_loop_variable_names, ForVariableNames
from tackle import tackle, new_context, HookCallInput


@pytest.mark.parametrize("input_string,public_data,index_name,value_name,key_name", [
    ("foo", {'foo': []}, 'index', 'item', None),
    ("i, v in foo", {'foo': []}, 'i', 'v', None),
    ("i in foo", {'foo': []}, 'index', 'i', None),
    ("foo", {'foo': {}}, 'index', 'value', "key"),
    ("k in foo", {'foo': {}}, 'index', 'value', "k"),
    ("k, v in foo", {'foo': {}}, 'index', 'v', "k"),
    ("k, v, i in foo", {'foo': {}}, 'i', 'v', "k"),
])
def test_parser_get_for_loop_variable_names(
        input_string,
        public_data,
        index_name,
        value_name,
        key_name,
):
    context = new_context()
    context.data.public = public_data
    hook_call = HookCallInput(for_=input_string)
    output = get_for_loop_variable_names(context, hook_call)

    assert output.index_name == index_name
    assert output.value_name == value_name
    assert output.key_name == key_name


def test_parser_multiple_args(cd_fixtures):
    """Test input args."""
    output = tackle('args.yaml', no_input=True)
    assert output['two_args'] == 'foo bar'
    assert output['three_args'] == 'foo bar baz'


def test_parser_tackle_in_tackle(cd):
    cd('parse')
    output = tackle('outer-tackle.yaml', no_input=True)
    assert output['outer']['foo_items'] == ['bar', 'baz']


def test_parser_tackle_in_tackle_arg(cd):
    cd('parse')
    output = tackle('outer-tackle-arg.yaml', no_input=True)
    assert output['outer']['foo_items'] == ['bar', 'baz']


def test_parser_duplicate_values(cd_fixtures):
    """
    Validate that when we give a hook with duplicate values as what was set in the
     initial run (ie a tackle hook with `no_input` set), that we take the value from the
     hook.
    """
    output = tackle('duplicate-values.yaml', verbose=True)
    assert output['local']['two_args']


def test_parser_hook_args_not_copied(cd_fixtures):
    """
    When calling a hook with an arg, there was an issue with the hook's args being
     copied from one hook call to the next of the same hook suggesting the hook was not
     copied when called. This is to check that.
    """
    output = tackle('copied-hook-args.yaml')
    assert output['upper'].isupper()
    assert output['lower'].islower()
    assert output['lower_default'].islower()


def test_parser_bool_value_defaults(cd_fixtures):
    """Check that when a bool field is default to true that raising flag inverts it."""
    output = tackle('bool-hooks.yaml', hooks_dir='bool-hooks')

    assert output['call']['is_true']
    assert not output['call']['is_false']
    assert not output['call_true']['is_true']
    assert output['call_true']['is_false']


def test_parser_no_exec_python(cd_fixtures):
    """Check that when a python hook has no exec that it still validates and returns."""
    output = tackle('MyHook', hooks_dir='no-exec')

    assert output['is_true']
    assert not output['is_false']
