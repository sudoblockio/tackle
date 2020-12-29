"""Tests around using locally cached cookiecutter template repositories."""

import os

import pytest

from tackle import repository, exceptions
from tests.repository import update_source_fixtures


def test_finds_local_repo(change_dir_main_fixtures, tmpdir):
    """A valid local repository should be returned."""
    source, mode, settings = update_source_fixtures(
        'fake-repo',
        abbreviations={},
        clone_to_dir=str(tmpdir),
        checkout=None,
        no_input=True,
    )
    repository.update_source(source=source, mode=mode, settings=settings)

    assert 'fake-repo' == os.path.basename(source.repo_dir)
    assert source.context_file == 'cookiecutter.json'
    assert not source.cleanup


def test_local_repo_with_no_context_raises(tmpdir, change_dir_main_fixtures):
    """A local repository without a cookiecutter.json should raise a \
    `RepositoryNotFound` exception."""
    template_path = os.path.abspath('fake-repo-bad')
    with pytest.raises(exceptions.RepositoryNotFound) as err:
        source, mode, settings = update_source_fixtures(
            template_path,
            abbreviations={},
            clone_to_dir=str(tmpdir),
            checkout=None,
            no_input=True,
        )
        repository.update_source(source=source, mode=mode, settings=settings)

    assert (
        f'A valid repository for "{template_path}" could not be found in the following'
        in str(err.value)
    )
    # assert str(err.value) == (
    #     'A valid repository for "{}" could not be found in the following '
    #     'locations:\n{}'.format(
    #         template_path,
    #         '\n'.join(
    #             [template_path, str(tmpdir / 'tests/legacy/fixtures/fake-repo-bad')]
    #         ),
    #     )
    # )


def test_local_repo_typo(tmpdir, change_dir_main_fixtures):
    """An unknown local repository should raise a `RepositoryNotFound` \
    exception."""
    template_path = 'unknown-repo'
    with pytest.raises(exceptions.RepositoryNotFound) as err:
        source, mode, settings = update_source_fixtures(
            template_path,
            abbreviations={},
            clone_to_dir=str(tmpdir),
            checkout=None,
            no_input=True,
        )
        repository.update_source(source=source, mode=mode, settings=settings)

    assert (
        f'A valid repository for "{template_path}" could not be found in the following'
        in str(err.value)
    )

    # assert str(err.value) == (
    #     'A valid repository for "{}" could not be found in the following '
    #     'locations:\n{}'.format(
    #         template_path,
    #         '\n'.join([template_path, str(tmpdir / 'tests/unknown-repo')]),
    #     )
    # )
