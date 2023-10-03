import pytest

from tackle import tackle


def test_provider_logic_type():
    """Check type works."""
    output = tackle('type.yaml')
    assert output['str_type'] == 'str'
    assert output['list_type'] == 'list'
    assert output['a_dict_type'] == 'dict'
    assert output['dict_list_type'] == 'dict'
    assert output['list_dict_type'] == 'list'
    assert output['with_args']['type'] == 'list'
    assert output['default']['type'] == 'list'

TYPE_FIXTURES = [
    ("str", "str"),
    ("list", "list"),
]

@pytest.mark.parametrize("fixture_name,expected_output", TYPE_FIXTURES)
def test_provider_types_parameterized(cd, fixture_name, expected_output):
    """Check type works."""
    cd('type-fixtures')
    output = tackle(f'{fixture_name}.yaml')
    assert output[f'{fixture_name}_type'] == expected_output



def test_hook_casting():
    """Check casting works."""
    output = tackle('castings.yaml')
    # Assertions in file
    assert output
