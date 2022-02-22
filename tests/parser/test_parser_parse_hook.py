"""High level tests for parser logic."""
import pytest
import yaml

from tackle.main import tackle


FIXTURES = [
    ('map.yaml', 'map-output.yaml'),
    ('map-lists.yaml', 'map-lists-output.yaml'),
    ('arg-types.yaml', 'arg-types-output.yaml'),
    ('empty-elements.yaml', 'empty-elements.yaml'),
    ('private-context.yaml', 'private-context-output.yaml'),
    ('map-root.yaml', 'map-root-output.yaml'),
    ('private-hooks.yaml', 'private-hooks-output.yaml'),
    ('outer-tackle.yaml', 'outer-tackle-output.yaml'),
    ('outer-tackle-list.yaml', 'outer-tackle-list-output.yaml'),
    ('merge-simple.yaml', 'merge-simple-output.yaml'),
    ('merge-petstore-compact.yaml', 'petstore.yaml'),
    # # Non tackle things
    ('k8s-deployment.yaml', 'k8s-deployment.yaml'),
    ('ansible-playbook.yaml', 'ansible-playbook.yaml'),
    ('docker-compose.yml', 'docker-compose.yml'),
    ('list-list.yaml', 'list-list.yaml'),
    ('var-hook.yaml', 'var-hook-output.yaml'),
    # # Broken
    # ('document-hooks.yaml', 'outer_tackle_expected.yaml'),
]


@pytest.mark.parametrize("fixture,expected_output", FIXTURES)
def test_main_expected_output(change_curdir_fixtures, fixture, expected_output):
    """Input equals output."""
    with open(expected_output) as f:
        expected_output = yaml.safe_load(f)

    output = tackle(fixture)
    assert output == expected_output
