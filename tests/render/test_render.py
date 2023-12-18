import pytest

from tackle import tackle
from tackle.factory import new_context
from tackle.render import add_jinja_hook_to_jinja_globals, render_string
from tackle.utils.files import read_config_file


def test_render_types(cd_fixtures):
    """Check that types are respected."""
    output = tackle('types.yaml')
    # assert output['hex'] == '0x1'
    assert output['float'] == 1.0
    assert isinstance(output['bool'], bool)

    assert isinstance(output['int'], int)
    assert isinstance(output['float'], float)
    # assert isinstance(output['hex'], str)
    assert isinstance(output['bool'], bool)

    assert output['bool'] == output['bool_render']
    assert output['int'] == output['int_render']
    assert output['float'] == output['float_render']


RENDERABLES = [
    # This test relates to https://github.com/pallets/jinja/issues/1580 where if we have
    # a variable that collides with a jinja globals it is ignored
    # https://github.com/robcxyz/tackle/issues/19
    ({'dict': {'stuff': 'things'}}, '{{dict}}', {'stuff': 'things'}),
    ({'input': {'stuff': 'things'}}, '{{input}}', {'stuff': 'things'}),
    ({'input': 3}, '{{input % 3 == 0}}', True),
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
    ("no_exec", "{{no_exec()}}", {'foo': 'bar'}),
    ("no_exec", "{{no_exec(foo='baz')}}", {'foo': 'baz'}),
    ("no_exec_arg", "{{no_exec_arg('baz')}}", {'foo': 'baz'}),
    ("with_exec", "{{with_exec()}}", {'baz': 'bar'}),
    ("with_exec", "{{with_exec(foo='bar')}}", {'baz': 'bar'}),
    ("with_exec", "{{with_exec('bar')}}", {'baz': 'bar'}),
    ("with_method", "{{with_method.a_method()}}", {'bin': 'bar', 'din': 'ban'}),
    ("with_method", "{{with_method.a_method('fin')}}", {'bin': 'fin', 'din': 'ban'}),
    (
        "with_method",
        "{{with_method.a_method(foo='fin')}}",
        {'bin': 'fin', 'din': 'ban'},
    ),
    (
        "with_method_multiple_args",
        "{{with_method_multiple_args.a_method('fin')}}",
        {'bin': 'bar', 'din': 'fin'},
    ),
    (
        "embedded_methods",
        "{{embedded_methods.a_method.b_method('fin')}}",
        {'bin': 'bar', 'din': 'ban', 'lin': 'fin'},
    ),
]


@pytest.mark.parametrize("hook_name,render_input,expected_output", METHOD_ADD_FIXTURES)
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


def test_render_jinja_filter_builtins(cd_fixtures):
    """Make sure we can still use jinja's builtin filters."""
    o = tackle('jinja-builtins.yaml')

    assert o['jinja_filter'] == 2


@pytest.mark.parametrize("render_var", [1, 1.1, '1', '1.2'])
def test_render_preserve_types(context, render_var):
    """ """
    context.data.public = {'var1': render_var}
    output = render_string(context, raw='{{ var1 }}')

    assert output == render_var


@pytest.mark.parametrize(
    "raw,render_context,expected_output",
    [
        ('{{var1 + var2}}', {'var1': 1, 'var2': 1}, 2),
        ('{{var1 + var2}}', {'var1': 1, 'var2': 1.2}, 2.2),
        ('{{var1 + var2}}', {'var1': 1.2, 'var2': 1}, 2.2),
        ('{{var1 and var2}}', {'var1': True, 'var2': '1'}, True),
        ('{{var1 and var2}}', {'var1': 1, 'var2': True}, True),
        ('{{var1 == var2}}', {'var1': 1, 'var2': 1}, True),
        # Broken
        # ('{{var1 + var2}}', {'var1': '1', 'var2': '1'}, '11'),
        # ('{{var1 + str(var2)}}', {'var1': '1', 'var2': 1}, '11'),
    ],
)
def test_render_preserve_types_jinja_logic(
    context, raw, render_context, expected_output
):
    """
    Check that when we have multiple variables that we can do arithmatic and get the
     right type out.
    """
    context.data.public = render_context
    output = render_string(context, raw=raw)

    assert output == expected_output
