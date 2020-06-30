"""Tests for `repository_has_cookiecutter_json` function."""
import pytest

from cookiecutter.repository import repository_has_cookiecutter_json


def test_valid_repository():
    """Validate correct response if `cookiecutter.json` file exist."""
    assert repository_has_cookiecutter_json('tests/fake-repo')


@pytest.mark.parametrize(
    'invalid_repository', (['tests/fake-repo-bad', 'tests/unknown-repo'])
)
def test_invalid_repository(invalid_repository):
    """Validate correct response if `cookiecutter.json` file not exist."""
    assert not repository_has_cookiecutter_json(invalid_repository)


@pytest.mark.parametrize(
    'valid_repository',
    (['tests/fixtures/valid/nuki-input', 'tests/fixtures/valid/yaml-input']),
)
def test_valid_repositories_yaml_nuki(valid_repository):
    """Validate generic reader works properly."""
    assert repository_has_cookiecutter_json(valid_repository)
