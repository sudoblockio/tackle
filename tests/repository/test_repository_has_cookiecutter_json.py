"""Tests for `repository_has_cookiecutter_json` function."""
import pytest

from tackle.repository import repository_has_tackle_file


def test_valid_repository(change_dir_main_fixtures):
    """Validate correct response if `cookiecutter.json` file exist."""
    assert repository_has_tackle_file('fake-repo')


@pytest.mark.parametrize(
    'invalid_repository', (['fake-repo-bad', 'tests/unknown-repo']),
)
def test_invalid_repository(invalid_repository, change_dir_main_fixtures):
    """Validate correct response if `cookiecutter.json` file not exist."""
    assert not repository_has_tackle_file(invalid_repository)


@pytest.mark.parametrize(
    'valid_repository', (['valid/tackle-input', 'valid/yaml-input']),
)
def test_valid_repositories_yaml_tackle(valid_repository, change_dir_main_fixtures):
    """Validate generic reader works properly."""
    assert repository_has_tackle_file(valid_repository)
