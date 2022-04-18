import pytest

from tackle.models import Context
from tackle.render import render_string
from tackle import tackle
from tackle.utils.files import read_config_file


RENDERABLES = [
    # This test relates to https://github.com/pallets/jinja/issues/1580 where if we have
    # a variable that collides with a jinja globals it is ignored
    # https://github.com/robcxyz/tackle-box/issues/19
    ({'dict': {'stuff': 'things'}}, '{{dict}}', {'stuff': 'things'}),
    ({'namespace': {'stuff': 'things'}}, '{{namespace}}', {'stuff': 'things'}),
    # Normal
    ({'adict': {'stuff': 'things'}}, '{{adict}}', {'stuff': 'things'}),
    ({'list': ['stuff', 'things']}, '{{list}}', ['stuff', 'things']),
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
