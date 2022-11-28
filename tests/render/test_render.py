import pytest

from tackle.models import Context
from tackle.render import render_string
from tackle import tackle
from tackle.utils.files import read_config_file


RENDERABLES = [
    # This test relates to https://github.com/pallets/jinja/issues/1580 where if we have
    # a variable that collides with a jinja globals it is ignored
    # https://github.com/robcxyz/tackle/issues/19
    ({'dict': {'stuff': 'things'}}, '{{dict}}', {'stuff': 'things'}),
    ({'namespace': {'stuff': 'things'}}, '{{namespace}}', {'stuff': 'things'}),
    # Normal
    ({'adict': {'stuff': 'things'}}, '{{adict}}', {'stuff': 'things'}),
    ({'list': ['stuff', 'things']}, '{{list}}', ['stuff', 'things']),
    # Dashes don't work ->
    # ({'a-dash': 'dash'}, '{{a-dash}}', 'dash'),
]


@pytest.mark.parametrize("context,raw,expected_output", RENDERABLES)
def test_render_string_inputs(context, raw, expected_output):
    context = Context(public_context=context)
    output = render_string(context=context, raw=raw)

    assert output == expected_output


FILES = [
    # TODO: Not asserting - RM
    # ('multi-line-block.yaml', 'multi-line-block-output.yaml'),
    ('call-function.yaml', 'call-function-output.yaml'),
]


@pytest.mark.parametrize("file,expected_output", FILES)
def test_render_files(change_curdir_fixtures, file, expected_output):
    o = tackle(file)
    expected_output = read_config_file(expected_output)
    assert o == expected_output


def test_render_hook_call_multiple(change_curdir_fixtures):
    """
    Check that when we run a hook multiple times, that we don't carry over the prior
    hook calls arguments which may not be instantiated on the second hook call. This
    happens when the hook that was called is left in the jinja env's globals and not
    removed which makes the hook not an `unknown_variable` so it uses the prior args.
    """
    o = tackle('multiple-hook-renders.yaml')
    assert o['first'] == "foo,stuff"
    assert o['second'] == "2.txt"
