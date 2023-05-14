import pytest

from tackle import tackle


@pytest.fixture()
def fixture_dir(chdir):
    chdir("composition-fixtures")


def test_functions_composition_enum_basic(fixture_dir):
    """
    Show that we can create enum types, that they fail when we give them some value
     out of its members, and that it is properly deserialized.
    """
    output = tackle('enum-basic.yaml')

    assert output['failure']
    assert output['failure_default']

    assert output['success']['color'] == 'blue'
    assert output['success']['color_default'] == 'red'
    assert output['success_default']['color'] == 'blue'
    assert output['success_default']['color_default'] == 'green'


def test_functions_composition_enum_basic_1(fixture_dir):
    output = tackle('scratch.yaml')

    assert output
