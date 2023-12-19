import pytest

from tackle import get_hook, tackle
from tackle.factory import new_context
from tackle.models import HookCallInput
from tackle.parser import run_hook_exec, split_input_data

SPLIT_INPUT_FIXTURES: list[tuple[dict, tuple[int, int, int]]] = [
    (
        {
            'pre': 1,
            'a_hook<-': {1: 1},
            'post': 1,
        },
        (1, 1, 1),
    ),
    (
        {
            'pre1': 1,
            'pre2': 1,
            'a_hook_1<-': {1: 1},
            'post1': 1,
            'a_hook_2<-': {1: 1},
            'post2': 1,
        },
        (2, 2, 2),
    ),
    (
        {
            'a_hook_1<-': {1: 1},
            'post1': 1,
            'post2': 1,
            'post3': 1,
            'a_hook_2<-': {1: 1},
            'post4': 1,
        },
        (0, 4, 2),
    ),
    (
        {
            'a_hook_1<-': {1: 1},
            'post1': 1,
            'post2': 1,
            'post3': 1,
            'a_hook_2<-': {1: 1},
        },
        (0, 3, 2),
    ),
    (
        {
            'a_hook_1<-': {1: 1},
        },
        (0, 0, 1),
    ),
]


@pytest.mark.parametrize("raw_input,counts", SPLIT_INPUT_FIXTURES)
def test_parser_split_input_data(raw_input, counts):
    context = new_context()
    context.data.raw_input = raw_input
    split_input_data(context=context)

    assert len(context.data.pre_input) == counts[0]
    assert len(context.data.post_input) == counts[1]
    assert len(context.hooks.public) == counts[2]


# @pytest.mark.parametrize("hook_input,expected_output", [
#     ('do<-', True),
#     ('()do<-', True),
#     ('(foo)do<-', True),
#     ('(b bar)do<-', True),
#     ('(a)do(b)<-', True),
#     ('(a)do(b list[str])<-', True),
#     ('do(foo)<-', True),
#     ('do(b bar)<-', True),
#     ('do(b int = 1)<-', True),
#     ('do(b list[str])<-', True),
# ])
# def test_parser_is_hook(hook_input, expected_output):
#     assert is_dcl_hook(hook_input) == expected_output


def test_parser_run_hook_exec():
    """When a hook is called that does not need any supplied params it works."""
    context = new_context()
    context.data.public = {'foo': 'bar'}
    hook = get_hook('literal')(input='foo')
    hook_call = HookCallInput()

    output = run_hook_exec(context=context, hook_call=hook_call, hook=hook)
    assert output == 'foo'


def test_parser_run_hook_exec_context():
    """When a hook is called that does need supplied params such as context it works."""
    context = new_context()
    context.data.public = {'foo': 'bar'}
    hook = get_hook('set')(path='foo', value='baz')
    hook_call = HookCallInput()

    run_hook_exec(context=context, hook_call=hook_call, hook=hook)
    assert context.data.public['foo'] == 'baz'


def test_parser_run_hook_exec_context_quoted():
    """
    Sometimes the user will be quoting the type - ie def call(self, context: 'Context')
     so we need to account for this.
    """
    context = new_context()
    context.data.public = {'foo': 'bar'}
    hook = get_hook('var')(input='{{foo}}')
    hook_call = HookCallInput()

    output = run_hook_exec(context=context, hook_call=hook_call, hook=hook)
    assert output == 'bar'


def test_parser_multiple_args(cd_fixtures):
    """Test input args."""
    output = tackle('args.yaml', no_input=True)

    assert output['two_args'] == 'foo bar'
    assert output['three_args'] == 'foo bar baz'


def test_parser_tackle_in_tackle(cd):
    """Check that we can call a tackle within a tackle."""
    cd('parse')
    output = tackle('outer-tackle.yaml', no_input=True)

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
