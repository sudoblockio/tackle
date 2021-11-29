"""High level tests for parser logic."""
import pytest
import yaml

from tackle.main import tackle

FIXTURES = [
    ('tackle_map.yaml', 'tackle_map_output.yaml'),
    ('tackle_map_lists.yaml', 'tackle_map_lists_output.yaml'),
    ('tackle_map_root.yaml', 'tackle_map_root_output.yaml'),
    ('outer_tackle.yaml', 'outer_tackle_expected.yaml'),
    # Non tackle things
    ('k8s-deployment.yaml', 'k8s-deployment.yaml'),
    ('docker-compose.yml', 'docker-compose.yml'),
]


@pytest.mark.parametrize("fixture,expected_output", FIXTURES)
def test_main_expected_output(change_curdir_fixtures, fixture, expected_output):
    """Input equals output."""
    with open(expected_output) as f:
        expected_output = yaml.safe_load(f)

    output = tackle(fixture)
    assert dict(output) == expected_output
