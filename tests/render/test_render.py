import pytest

from tackle.models import Context
from tackle.render import render_string


RENDERABLES = [
    # This test relates to https://github.com/pallets/jinja/issues/1580 where if we have
    # a variable that collides with a jinja globals it is ignored
    # https://github.com/robcxyz/tackle-box/issues/19
    # ({'dict': {'stuff': 'things'}}, '{{dict}}', {'stuff': 'things'}),
    ({'adict': {'stuff': 'things'}}, '{{adict}}', {'stuff': 'things'}),
    ({'list': ['stuff', 'things']}, '{{list}}', ['stuff', 'things']),
]


@pytest.mark.parametrize("context,raw,expected_output", RENDERABLES)
def test_render_string_inputs(context, raw, expected_output):
    context = Context(output_dict=context)
    output = render_string(context=context, raw=raw)

    assert output == expected_output
