"""Tests for `repository_has_cookiecutter_json` function."""
import pytest

from cookiecutter.repository import repository_has_tackle_file


def test_valid_repository():
    """Validate correct response if `cookiecutter.json` file exist."""
    assert repository_has_tackle_file('tests/legacy/fixtures/fake-repo')


@pytest.mark.parametrize(
    'invalid_repository',
    (['tests/legacy/fixtures/fake-repo-bad', 'tests/unknown-repo']),
)
def test_invalid_repository(invalid_repository):
    """Validate correct response if `cookiecutter.json` file not exist."""
    assert not repository_has_tackle_file(invalid_repository)


@pytest.mark.parametrize(
    'valid_repository',
    (
        [
            'tests/legacy/fixtures/valid/nuki-input',
            'tests/legacy/fixtures/valid/yaml-input',
        ]
    ),
)
def test_valid_repositories_yaml_nuki(valid_repository):
    """Validate generic reader works properly."""
    assert repository_has_tackle_file(valid_repository)
