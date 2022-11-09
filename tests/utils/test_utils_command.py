"""Test for tackle.utils.command"""
import pytest

from tackle.utils.command import unpack_args_kwargs_string, split_input_string

INPUT_STRINGS = [
    ('this --if "expanded == \'that\'"', ['this', '--if', "expanded == 'that'"]),
    ('this that', ['this', 'that']),
    ('this ["foo","bar"]', ['this', ["foo", "bar"]]),
    ('this {"foo":"bar"}', ['this', {"foo": "bar"}]),
    ('{"foo":"bar"} this', [{"foo": "bar"}, 'this']),
    (
        '["this"] --if "expanded == \'that\'"',
        [["this"], '--if', "expanded == \'that\'"],
    ),
    (
        '["this","and","that"] --if "expanded == \'that\'"',
        [["this", "and", "that"], '--if', "expanded == \'that\'"],
    ),
    (
        '{"this":"and"} --if "expanded == \'that\'"',
        [{"this": "and"}, '--if', "expanded == \'that\'"],
    ),
    (
        '{"this":"and","that":"and"} --if "expanded == \'that\'"',
        [{"this": "and", "that": "and"}, '--if', "expanded == \'that\'"],
    ),
    (
        "{'this':'and','that':'and'} --if 'expanded == \"that\"'",
        [{"this": "and", "that": "and"}, '--if', "expanded == \"that\""],
    ),
    (
        "{{get('stuff-and')}}",
        ["{{get(\'stuff-and\')}}"],
    ),
    (
        "{{get('stuff-and',sep='-')}}",
        ["{{get(\'stuff-and\',sep=\'-\')}}"],
    ),
    # TODO: Fix splitting on whitespace unless it is surrounded by special chars
    #  Or just replace with pyparsing ->
    # (
    #     "{{print('things', 'stuff')}}",
    #     ["{{print(\'things\', \'stuff\')}}"],
    # ),
]


@pytest.mark.parametrize("input_string,expected_output", INPUT_STRINGS)
def test_utils_command_split_input_string(input_string, expected_output):
    output = split_input_string(input_string)
    assert output == expected_output


TEMPLATES = [
    # # template, len_args, len_kwargs, len_flags
    ('foo bar baz', 3, 0, 0),
    ('foo --bar baz bing', 2, 1, 0),
    ('foo bar --baz foo', 2, 1, 0),
    ('foo bar --baz foo --bing baz', 2, 2, 0),
    ('foo --bar baz', 1, 1, 0),
    ('foo bar --baz', 2, 0, 1),
    ('foo bar baz --bing', 3, 0, 1),
    ('foo --bar baz --foo', 1, 1, 1),
    ('foo bar --foo bar --bing --baz bling', 2, 2, 1),
    ('foo --bar baz blah --bling', 2, 1, 1),
    ('this --if "expanded == \'that\'"', 1, 1, 0),
    ('["this"] --if "expanded == \'that\'"', 1, 1, 0),
    ('["this"] ["this"] --if "expanded == \'that\'"', 2, 1, 0),
    ('["this"] --for ["this"] --if "expanded == \'that\'"', 1, 2, 0),
    ('"this --if" --if "expanded == \'that\'"', 1, 1, 0),
    ('var {{print("things")}}', 2, 0, 0),
    ('tackle secrets.yaml --if isfile(path_join([cwd,\'secrets.yaml\']))', 2, 1, 0),
    # For inputs with `=` signs -> Need to modify insane regex (ugh)
    # -> or move to peg parser
    # ('foo --bar=baz bing', 2, 1, 0),
    # ('foo bar --baz=foo', 2, 1, 0),
    # ('foo bar --baz=foo --bing=baz', 2, 2, 0),
    # ('foo --bar=baz', 1, 1, 0),
    # ('foo --bar=baz --foo', 1, 1, 1),
    # ('foo bar --foo=bar --bing --baz bling', 2, 2, 1),
    # ('foo --bar=baz blah --bling', 2, 1, 1),
    # ('foo --bar= baz blah --bling', 2, 1, 1),
    # ('foo --bar = baz blah --bling', 2, 1, 1),
]


@pytest.mark.parametrize("template,len_args,len_kwargs,len_flags", TEMPLATES)
def test_unpack_args_kwargs(template, len_args, len_kwargs, len_flags):
    """Validate the count of each input arg/kwarg/flag."""
    args, kwargs, flags = unpack_args_kwargs_string(template)

    assert len_args == len(args)
    assert len_kwargs == len(kwargs)
    assert len_flags == len(flags)


FIXTURES = [
    # input_string, args, kwargs, flags
    ("this --if \"expanded == 'that'\"", ["this"], {"if": "expanded == 'that'"}, []),
    (
        "this that --if \"expanded == 'that'\"",
        ["this", "that"],
        {"if": "expanded == 'that'"},
        [],
    ),
]


@pytest.mark.parametrize("input_string,args,kwargs,flags", FIXTURES)
def test_unpack_input_string(input_string, args, kwargs, flags):
    """Validate expressions for input strings."""
    args_out, kwargs_out, flags_out = unpack_args_kwargs_string(input_string)
    assert args_out == args
    assert kwargs_out == kwargs
    assert flags_out == flags
