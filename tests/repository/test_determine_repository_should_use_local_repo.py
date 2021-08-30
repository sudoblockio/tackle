"""Tests around using locally cached cookiecutter template repositories."""

import os

import pytest

from tackle import exceptions
from tests.repository import update_source_fixtures


def test_finds_local_repo(change_dir_main_fixtures, tmpdir):
    """A valid local repository should be returned."""
    context = update_source_fixtures(
        template='fake-repo',
        abbreviations={},
        clone_to_dir=str(tmpdir),
        checkout=None,
        no_input=True,
    )
    context.update_source()

    assert 'fake-repo' == os.path.basename(context.repo_dir)
    assert context.context_file == 'cookiecutter.json'
    assert not context.cleanup


def test_local_repo_with_no_context_raises(tmpdir, change_dir_main_fixtures):
    """A local repository without a cookiecutter.json should raise a \
    `RepositoryNotFound` exception."""
    template_path = os.path.abspath('fake-repo-bad')
    with pytest.raises(exceptions.RepositoryNotFound) as err:
        context = update_source_fixtures(
            template=template_path,
            abbreviations={},
            clone_to_dir=str(tmpdir),
            checkout=None,
            no_input=True,
        )
        context.update_source()

    assert (
        f'A valid repository for "{template_path}" could not be found in the following'
        in str(err.value)
    )


def test_local_repo_typo_unknown(tmpdir, change_dir_main_fixtures):
    """An unknown local repository should raise a `RepositoryNotFound` \
    exception."""
    template_path = 'unknown-repo'
    with pytest.raises(exceptions.RepositoryNotFound) as err:
        context = update_source_fixtures(
            template=template_path,
            abbreviations={},
            clone_to_dir=str(tmpdir),
            checkout=None,
            no_input=True,
        )
        context.update_source()

    assert (
        f'A valid repository for "{template_path}" could not be found in the following'
        in str(err.value)
    )
