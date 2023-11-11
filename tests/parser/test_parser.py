import pytest

from tackle.main import tackle
from tackle.utils.command import unpack_args_kwargs_string
from tackle import tackle



FIXTURES = [
    ("this --if \"expanded == 'that'\"", ["this"], {"if": "expanded == 'that'"}, []),
    (
        "this that --if \"expanded == 'that'\"",
        ["this", 'that'],
        {"if": "expanded == 'that'"},
        [],
    ),
    (
        "this that --for i, v in thing",
        ["this", 'that'],
        {"for": "i, v in thing"},
        [],
    ),
    (
        "this that --for i, v in thing --try",
        ["this", 'that'],
        {"for": "i, v in thing"},
        ['try'],
    ),
]


@pytest.mark.parametrize("input_string,args,kwargs,flags", FIXTURES)
def test_unpack_input_string(input_string, args, kwargs, flags):
    """Verify the hook arguments."""
    args_out, kwargs_out, flags_out = unpack_args_kwargs_string(input_string)
    assert args_out == args
    assert kwargs_out == kwargs
    assert flags_out == flags


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
