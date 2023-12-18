import pytest

from tackle import tackle
from tackle.utils.files import read_config_file

FIXTURES = [
    # TODO: Fix for ordereddict output
    ('single-level.yaml', 'single-level-output.yaml'),
    ('nested-dict.yaml', 'nested-dict-output.yaml'),
    ('nested-for.yaml', 'nested-for-output.yaml'),
]


@pytest.mark.parametrize("input,output", FIXTURES)
def test_parser_blocks_validate_output(input, output):
    """Test blocks."""
    tackle_output = tackle(input)
    expected_output = dict(read_config_file(output))

    assert tackle_output == expected_output


def test_parser_macros_compact_hook_call_macro():
    """Check that embedded compact hooks are called appropriately."""
    output = tackle('compact-hook-macro.yaml')

    assert output['compact'] == 'things'


# # TODO: Can be fixed later if we get ruamel to parse unquoted templates but for now
# #  ruamel fails in the initial parsing with ConstructorError so nothing we can do
# #  in the macro to fix this.
# def test_parser_macros_ruamel_braces():
#     """
#     Validate super hack for ruamel parsing error where `stuff->: {{things}}`
#     (no quotes), ruamel interprets as:
#     'stuff': ordereddict([(ordereddict([('things', None)]), None)]).
#     """
#     output = tackle('ruamel-parsing-error-braces.yaml', verbose=True)
#     assert output['stuff'] == 'things'
#     assert output['a']['b'] is None
#     assert output['one'] == 'two'


def test_parser_macros_expanded_compact():
    """Check that both and expanded and compact expressions work in lists and dicts."""
    output = tackle('expanded-compact.yaml')

    assert output['expanded'] == 'bar'
    assert output['compact'] == 'bar'
    assert output['object']['expanded'] == 'bar'
    assert output['object']['compact'] == 'bar'
    assert output['list'][0]['expanded'] == 'bar'
    assert output['list'][0]['compact'] == 'bar'
    assert output['list'][1]['compact'] == 'bar'
    assert output['list'][1]['expanded'] == 'bar'
