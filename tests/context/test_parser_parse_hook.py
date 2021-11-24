import pytest
import yaml

from tackle.models import Context
from tackle.main import tackle

FIXTURES = [
    # ('tackle_map.yaml', 'tackle_map_output.yaml'),
    ('tackle_map_lists.yaml', 'tackle_map_output.yaml'),
    # ('tackle_map_root.yaml', 'tackle_map_root_output.yaml'),
    # ('tackle_import.yaml', 'petstore.yaml'),
]

@pytest.mark.parametrize("fixture,expected_output", FIXTURES)
def test_main_foo(change_curdir_fixtures, fixture, expected_output):
    with open(expected_output) as f:
        expected_output = yaml.safe_load(f)

    output = tackle(fixture)
    # assert dict(output) == expected_output
    from pprint import pprint
    pprint(output)