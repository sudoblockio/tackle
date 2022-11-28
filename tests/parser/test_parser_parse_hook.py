"""High level tests for parser logic."""
import pytest

from tackle.main import tackle
from tackle.utils.files import read_config_file

FIXTURES = [
    ('map.yaml', 'map-output.yaml'),
    ('map-lists.yaml', 'map-lists-output.yaml'),
    ('arg-types.yaml', 'arg-types-output.yaml'),
    ('empty-elements.yaml', 'empty-elements.yaml'),
    ('map-root.yaml', 'map-root-output.yaml'),
    ('private-hooks.yaml', 'private-hooks-output.yaml'),
    ('outer-tackle.yaml', 'outer-tackle-output.yaml'),
    ('outer-tackle-list.yaml', 'outer-tackle-list-output.yaml'),
    ('merge-simple.yaml', 'merge-simple-output.yaml'),
    ('merge-petstore-compact.yaml', 'petstore.yaml'),
    ('private-context.yaml', 'private-context-output.yaml'),
    # Non tackle things
    ('k8s-deployment.yaml', 'k8s-deployment.yaml'),
    ('ansible-playbook.yaml', 'ansible-playbook.yaml'),
    ('docker-compose.yml', 'docker-compose.yml'),
    ('list-list.yaml', 'list-list.yaml'),
    ('var-hook.yaml', 'var-hook-output.yaml'),
    ('toml.toml', 'toml.yaml'),
    # # Broken
    # # TODO: https://github.com/robcxyz/tackle/issues/52
    # ('bug-mixed-flags.yaml', 'bug-mixed-flags.yaml'),
    # ('document-hooks.yaml', 'document-hooks-expected.yaml'),
]


@pytest.mark.parametrize("fixture,expected_output", FIXTURES)
def test_main_expected_output(change_curdir_fixtures, fixture, expected_output):
    """Input equals output."""
    expected_output = read_config_file(expected_output)
    output = tackle(fixture)
    assert output == expected_output


def test_parser_ruamel_braces(change_curdir_fixtures):
    """
    Validate super hack for ruamel parsing error where `stuff->: {{things}}`
    (no quotes), ruamel interprets as:
    'stuff': ordereddict([(ordereddict([('things', None)]), None)]).
    """
    output = tackle('ruamel-parsing-error-braces.yaml', verbose=True)
    assert output['stuff'] == 'things'
    assert output['a']['b'] is None
    assert output['one'] == 'two'


def test_parser_duplicate_values(change_curdir_fixtures):
    """
    Validate that when we give a hook with duplicate values as what was set in the
     initial run (ie a tackle hook with `no_input` set), that we take the value from the
     hook.
    """
    output = tackle('duplicate-values.yaml', verbose=True)
    assert output['local']['two_args']
