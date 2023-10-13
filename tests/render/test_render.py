import pytest

from tackle.render import render_string, add_jinja_hook_to_jinja_globals
from tackle import tackle
from tackle.factory import new_context
from tackle.utils.files import read_config_file

RENDERABLES = [
    # This test relates to https://github.com/pallets/jinja/issues/1580 where if we have
    # a variable that collides with a jinja globals it is ignored
    # https://github.com/robcxyz/tackle/issues/19
    ({'dict': {'stuff': 'things'}}, '{{dict}}', {'stuff': 'things'}),
    ({'namespace': {'stuff': 'things'}}, '{{namespace}}', {'stuff': 'things'}),
    ({'namespace': 'foo'}, '{{namespace}}bar', 'foobar'),
    # Normal
    ({'adict': {'stuff': 'things'}}, '{{adict}}', {'stuff': 'things'}),
    ({'list': ['stuff', 'things']}, '{{list}}', ['stuff', 'things']),
    # Dashes don't work...
    # ({'a-dash': 'dash'}, '{{a-dash}}', 'dash'),
]


@pytest.mark.parametrize("input_context,raw,expected_output", RENDERABLES)
def test_render_string_inputs(input_context, raw, expected_output):
    context = new_context(existing_data=input_context)
    output = render_string(context=context, raw=raw)

    assert output == expected_output


FILES = [
    # TODO: Not asserting - RM
    # ('multi-line-block.yaml', 'multi-line-block-output.yaml'),
    ('call-function.yaml', 'call-function-output.yaml'),
    ('render-with-filters.yaml', 'render-with-filters-output.yaml'),
]


@pytest.mark.parametrize("file,expected_output", FILES)
def test_render_files(cd_fixtures, file, expected_output):
    o = tackle(file)
    expected_output = dict(read_config_file(expected_output))
    assert o == expected_output


METHOD_ADD_FIXTURES = [
    ("no_exec", "{{no_exec()}}", "{'foo': 'bar'}"),
    ("no_exec", "{{no_exec(foo='baz')}}", "{'foo': 'baz'}"),
    ("no_exec_arg", "{{no_exec_arg('baz')}}", "{'foo': 'baz'}"),
    ("with_exec", "{{with_exec()}}", "{'baz': 'bar'}"),
    ("with_exec", "{{with_exec(foo='bar')}}", "{'baz': 'bar'}"),
    ("with_exec", "{{with_exec('bar')}}", "{'baz': 'bar'}"),
    ("with_method", "{{with_method.a_method()}}", "{'bin': 'bar', 'din': 'ban'}"),
    ("with_method", "{{with_method.a_method('fin')}}", "{'bin': 'fin', 'din': 'ban'}"),
    (
        "with_method",
        "{{with_method.a_method(foo='fin')}}",
        "{'bin': 'fin', 'din': 'ban'}"
    ),
    (
        "with_method_multiple_args",
        "{{with_method_multiple_args.a_method('fin')}}",
        "{'bin': 'bar', 'din': 'fin'}"
    ),
    (
        "embedded_methods",
        "{{embedded_methods.a_method.b_method('fin')}}",
        "{'bin': 'bar', 'din': 'ban', 'lin': 'fin'}"
    ),
]


@pytest.mark.parametrize("hook_name,render_input,expected_output",METHOD_ADD_FIXTURES)
def test_render_add_jinja_hook_to_jinja_globals(
        cd_fixtures,
        hook_name,
        render_input,
        expected_output,
):
    context = tackle('jinja-hook-insert.yaml', return_context=True)
    add_jinja_hook_to_jinja_globals(context=context, hook_name=hook_name, used_hooks=[])
    template = context.env_.from_string(render_input)
    rendered_template = template.render({})

    assert context.env_.globals[hook_name]
    assert rendered_template == expected_output


def test_render_hook_call_multiple(cd_fixtures):
    """
    Check that when we run a hook multiple times, that we don't carry over the prior
     hook calls arguments which may not be instantiated on the second hook call. This
     happens when the hook that was called is left in the jinja env's globals and not
     removed which makes the hook not an `unknown_variable` so it uses the prior args.
    """
    o = tackle('multiple-hook-renders.yaml')
    assert o['first'] == "foo,stuff"
    assert o['second'] == "2.txt"
