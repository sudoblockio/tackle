import pytest

from tackle.main import tackle
from tackle.utils.files import read_config_file

# NOTE: Splitting up tests on fixtures between those located in `parse-fixtures`  and
# `fixtures` directories respectively there are A, so many fixtures and B, some are
# common and others are only for the below comparison test.

PARSE_FIXTURES = [
    ('map.yaml', 'map-output.yaml'),
    ('map-lists.yaml', 'map-lists-output.yaml'),
    ('arg-types.yaml', 'arg-types-output.yaml'),
    ('empty-elements.yaml', 'empty-elements.yaml'),
    ('map-root.yaml', 'map-root-output.yaml'),
    ('private-hooks.yaml', 'private-hooks-output.yaml'),
    ('merge-simple.yaml', 'merge-simple-output.yaml'),
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


@pytest.mark.parametrize("fixture,expected_output", PARSE_FIXTURES)
def test_main_expected_output_parse_fixtures_dir(chdir, fixture, expected_output):
    """Input equals output."""
    chdir("parse-fixtures")

    expected_output = read_config_file(expected_output)
    output = tackle(fixture)
    assert output == expected_output


COMMON_FIXTURES = [
    ('outer-tackle.yaml', 'outer-tackle-output.yaml'),
    ('outer-tackle-list.yaml', 'outer-tackle-list-output.yaml'),
    ('merge-petstore-compact.yaml', 'petstore.yaml'),
    ('merge-petstore-compact.yaml', 'petstore.yaml'),
]


@pytest.mark.parametrize("fixture,expected_output", COMMON_FIXTURES)
def test_main_expected_output_common_fixtures_dir(chdir, fixture, expected_output):
    """Input equals output."""
    chdir('fixtures')

    expected_output = read_config_file(expected_output)
    output = tackle(fixture)
    assert output == expected_output


def test_parser_duplicate_values(change_curdir_fixtures):
    """
    Validate that when we give a hook with duplicate values as what was set in the
     initial run (ie a tackle hook with `no_input` set), that we take the value from the
     hook.
    """
    output = tackle('duplicate-values.yaml', verbose=True)
    assert output['local']['two_args']


def test_parser_hook_args_not_copied(change_curdir_fixtures):
    """
    When calling a hook with an arg, there was an issue with the hook's args being
     copied from one hook call to the next of the same hook suggesting the hook was not
     copied when called. This is to check that.
    """
    output = tackle('copied-hook-args.yaml')
    assert output['upper'].isupper()
    assert output['lower'].islower()
    assert output['lower_default'].islower()
