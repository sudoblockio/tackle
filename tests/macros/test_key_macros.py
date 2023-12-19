from typing import Any

import pytest

import tackle.macros.key_macros as km
from tackle import tackle
from tackle.macros.key_macros import var_hook_macro
from tackle.utils.command import unpack_args_kwargs_string

TEMPLATES = [
    # These should all have `var` prepended to the args as it is indicative of a render
    ('"{{foo}}" bar baz', 4, 0, 0),
    ('{{ foo }} bar baz', 4, 0, 0),
    ('{{ foo }} bar baz bing', 5, 0, 0),
    ('{{ foo}} bar baz', 4, 0, 0),
    ('{{foo }} bar baz', 4, 0, 0),
    ('{{ foo }}-foo bar baz', 4, 0, 0),
    ('bar-{{ foo }}-foo', 2, 0, 0),
    ('bar-{{ foo in var }}-foo', 2, 0, 0),
]


@pytest.mark.parametrize("template,len_args,len_kwargs,len_flags", TEMPLATES)
def test_unpack_args_kwargs_handle_leading_brackets(
    template, len_args, len_kwargs, len_flags
):
    """Validate the count of each input arg/kwarg/flag."""
    args, kwargs, flags = unpack_args_kwargs_string(template)
    # test the macro
    args = var_hook_macro(args)

    assert len_args == len(args)
    assert len_kwargs == len(kwargs)
    assert len_flags == len(flags)


SPECIAL_KEY_MACRO_FIXTURES: list[tuple[str, Any, dict]] = [
    # key,value,expected_value
    (
        'print->',
        'foo',
        {'->': 'print', 'objects': 'foo', 'skip_output': True},
    ),
    (
        'import->',
        'foo',
        {'->': 'import foo'},
    ),
    (
        'import->',
        [{'src': 'foo'}],
        {'->': 'import', 'src': [{'src': 'foo'}]},
    ),
    (
        'import->',
        {'src': 'foo'},
        {'->': 'import', 'src': 'foo'},
    ),
    (
        'block_dict->',
        {'for': 'things', 'foo': 'bar'},
        {'->': 'block', 'for': 'things', 'items': {'foo': 'bar'}},
    ),
    (
        'return->',
        True,
        {'->': 'return', 'value': True},
    ),
    (
        'return->',
        "true --if {{foo}}",
        {'->': 'return', 'value': True, 'if': "{{foo}}"},
    ),
    (
        'debug->',
        None,
        {'->': 'debug', 'key': None},
    ),
    (
        'rendered_list->',
        ['foo', 'bar'],
        {'->': 'literal', 'input': ['foo', 'bar']},
    ),
]


@pytest.mark.parametrize("key,value,expected_value", SPECIAL_KEY_MACRO_FIXTURES)
def test_key_macros_parameterized(context, key, value, expected_value):
    """Check that the key_macro expands special keys right."""
    _, output_value = km.key_macro(context, key=key, value=value)

    assert output_value == expected_value


def test_key_macros_embedded_var():
    """Check when we have an embedded variable rendering that it works."""
    output = tackle('embedded-var.yaml')
    assert output['foo']['bar'] == 'things'


@pytest.mark.parametrize(
    "input",
    [
        'non-quoted-var-string.yaml',  # Processed in walk_document
        'non-quoted-var-field.yaml',  # Processed in render_hook_vars
    ],
)
def test_key_macros_templated_var(input):
    """Check that we don't need to run a macro"""
    output = tackle(input)
    assert output['foo'] == 'things'
