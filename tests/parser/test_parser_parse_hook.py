"""High level tests for parser logic."""
import pytest
import yaml

from tackle.main import tackle


FIXTURES = [
    ('map.yaml', 'map-output.yaml'),
    ('map-lists.yaml', 'map-lists-output.yaml'),
    ('map-root.yaml', 'map-root-output.yaml'),
    ('outer-tackle.yaml', 'outer-tackle-output.yaml'),
    ('private-hooks.yaml', 'private-hooks-output.yaml'),
    # ('document-hooks.yaml', 'outer_tackle_expected.yaml'),
    ('outer-tackle.yaml', 'outer-tackle-output.yaml'),
    ('merge-simple.yaml', 'merge-simple-output.yaml'),
    ('merge-petstore.yaml', 'petstore.yaml'),
    # # Non tackle things
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
