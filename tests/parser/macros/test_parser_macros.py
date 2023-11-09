import pytest

from tackle import tackle
from tackle.utils.files import read_config_file
from tackle.exceptions import EmptyBlockException


@pytest.fixture()
def macro_fixture_dir(chdir):
    chdir("macro-fixtures")


FIXTURES = [
    # TODO: Fix for odereddict output
    # ('single-level.yaml', 'single-level-output.yaml'),
    ('nested-dict.yaml', 'nested-dict-output.yaml'),
    ('nested-for.yaml', 'nested-for-output.yaml'),
    # Consider RM - Too much stuff
    # ('ansible-parse-call.yaml', 'ansible-parse-output.yaml')
]


@pytest.mark.parametrize("input,output", FIXTURES)
def test_parser_blocks_validate_output(macro_fixture_dir, input, output):
    """Test blocks."""
    tackle_output = tackle(input)
    expected_output = dict(read_config_file(output))
    assert tackle_output == expected_output


ERROR_SOURCES = [
    ("empty-block-exception.yaml", EmptyBlockException),
]


@pytest.mark.parametrize("input_file,exception", ERROR_SOURCES)
def test_parser_raises_exceptions(macro_fixture_dir, input_file, exception):
    """Validate that exceptions are raised."""
    with pytest.raises(exception):
        tackle(input_file)


def test_parser_calling_directory_preserve(macro_fixture_dir):
    """Validate that the calling_directory param is carried over from hook calls."""
    output = tackle('calling-context.yaml')
    assert output['call']['call']['calling_file'] == 'calling-context.yaml'


def test_parser_compact_hook_call_macro(macro_fixture_dir):
    """Check that embedded compact hooks are called appropriately."""
    output = tackle('compact-hook-macro.yaml')
    assert output['compact'] == 'things'


def test_parser_ruamel_braces(macro_fixture_dir):
    """
    Validate super hack for ruamel parsing error where `stuff->: {{things}}`
    (no quotes), ruamel interprets as:
    'stuff': ordereddict([(ordereddict([('things', None)]), None)]).
    """
    output = tackle('ruamel-parsing-error-braces.yaml', verbose=True)
    assert output['stuff'] == 'things'
    assert output['a']['b'] is None
    assert output['one'] == 'two'


def test_parser_macro_expanded_compact(macro_fixture_dir):
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