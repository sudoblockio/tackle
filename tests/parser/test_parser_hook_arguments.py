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


# TODO: When help is done
# @pytest.mark.parametrize("input_string", ['do_stuff', 'tackle.yaml do_stuff'])
# def test_parser_call_key_on_args(chdir_fixture, input_string):
#     """Validate that when an additional argument is supplied that the key is called."""
#     chdir_fixture('help')
#     output = tackle(input_string)
#     assert output['do_stuff'] == 'Doing things...'
#     assert output['do_things'] != 'Doing stuff...'


# @pytest.mark.parametrize(
#     "input_string",
#     [
#         # 'do_stuff',
#         # 'file.yaml do_stuff do_things'
#         'file.yaml do_stuff_compact do_things and other things'
#         # 'file.yaml do_stuff_compact_block print_this and print all this to'
#     ],
# )
# def test_parser_call_key_on_args_cli(chdir_fixture, input_string):
#     chdir_fixture('help')
#     main(input_string.split())
