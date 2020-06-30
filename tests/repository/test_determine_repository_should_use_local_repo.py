"""Tests around using locally cached cookiecutter template repositories."""

import os

import pytest

from cookiecutter import repository, exceptions


def test_finds_local_repo(monkeypatch, tmpdir):
    """A valid local repository should be returned."""
    test_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..')
    monkeypatch.chdir(test_dir)

    project_dir, context_file, cleanup = repository.determine_repo_dir(
        'tests/fake-repo',
        abbreviations={},
        clone_to_dir=str(tmpdir),
        checkout=None,
        no_input=True,
    )

    assert 'tests/fake-repo' == project_dir
    assert context_file == 'cookiecutter.json'
    assert not cleanup


def test_local_repo_with_no_context_raises(tmpdir):
    """A local repository without a cookiecutter.json should raise a \
    `RepositoryNotFound` exception."""
    template_path = os.path.join('tests', 'fake-repo-bad')
    with pytest.raises(exceptions.RepositoryNotFound) as err:
        repository.determine_repo_dir(
            template_path,
            abbreviations={},
            clone_to_dir=str(tmpdir),
            checkout=None,
            no_input=True,
        )

    assert str(err.value) == (
        'A valid repository for "{}" could not be found in the following '
        'locations:\n{}'.format(
            template_path,
            '\n'.join([template_path, str(tmpdir / 'tests/fake-repo-bad')]),
        )
    )


def test_local_repo_typo(tmpdir):
    """An unknown local repository should raise a `RepositoryNotFound` \
    exception."""
    template_path = os.path.join('tests', 'unknown-repo')
    with pytest.raises(exceptions.RepositoryNotFound) as err:
        repository.determine_repo_dir(
            template_path,
            abbreviations={},
            clone_to_dir=str(tmpdir),
            checkout=None,
            no_input=True,
        )

    assert str(err.value) == (
        'A valid repository for "{}" could not be found in the following '
        'locations:\n{}'.format(
            template_path,
            '\n'.join([template_path, str(tmpdir / 'tests/unknown-repo')]),
        )
    )
