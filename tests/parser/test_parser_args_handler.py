import pytest

from tackle import tackle
from tackle.parser import handle_leading_brackets
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
    args = handle_leading_brackets(args)

    assert len_args == len(args)
    assert len_kwargs == len(kwargs)
    assert len_flags == len(flags)


def test_parser_types(change_curdir_fixtures):
    output = tackle('types.yaml')
    assert isinstance(output['int'], int)
    # TODO:
    # assert isinstance(output['float'], float)
    # assert isinstance(output['bool'], bool)
