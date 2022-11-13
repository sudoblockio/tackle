"""Verify hook argument related items."""
import pytest
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
]


@pytest.mark.parametrize("input_string,args,kwargs,flags", FIXTURES)
def test_unpack_input_string(input_string, args, kwargs, flags):
    """Verify the hook arguments."""
    args_out, kwargs_out, flags_out = unpack_args_kwargs_string(input_string)
    assert args_out == args
    assert kwargs_out == kwargs
    assert flags_out == flags


def test_parser_multiple_args(change_curdir_fixtures):
    """Test input args."""
    output = tackle('args.yaml', no_input=True)
    assert output['two_args'] == 'foo bar'
    assert output['three_args'] == 'foo bar baz'


def test_parser_tackle_in_tackle(change_curdir_fixtures):
    """Test input args."""
    output = tackle('outer-tackle.yaml', no_input=True)
    assert output['outer']['foo_items'] == ['bar', 'baz']


def test_parser_tackle_in_tackle_arg(change_curdir_fixtures):
    """Test input args."""
    output = tackle('outer-tackle-arg.yaml', no_input=True)
    assert output['outer']['foo_items'] == ['bar', 'baz']


def test_parser_render_hook_input(change_curdir_fixtures):
    """
    Show that when the first argument is a renderable that you just render that with the
    context and logic.
    """
    output = tackle('var-hook.yaml', no_input=True)
    for k, v in output.items():
        if k.startswith('stuff'):
            assert v == 'things'
