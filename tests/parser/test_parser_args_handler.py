import pytest

from tackle import tackle

# from tackle.parser import handle_leading_brackets
from tackle.macros import var_hook_macro
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
    args = var_hook_macro(args)

    assert len_args == len(args)
    assert len_kwargs == len(kwargs)
    assert len_flags == len(flags)


def test_parser_types(change_curdir_fixtures):
    """Check that types are respected."""
    output = tackle('types.yaml')
    assert output['hex'] == '0x01'
    assert output['float'] == 1.0
    assert output['bool']

    assert isinstance(output['int'], int)
    assert isinstance(output['float'], float)
    assert isinstance(output['hex'], str)
    assert isinstance(output['bool'], bool)

    assert output['bool'] == output['bool_render']
    assert output['int'] == output['int_render']
    assert output['float'] == output['float_render']
    assert output['hex'] == output['hex_render']
