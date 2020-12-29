"""Collection of tests around cloning cookiecutter template repositories."""
import os

import pytest

from tackle import repository
from tackle import exceptions
from tests.repository import update_source_fixtures


@pytest.mark.parametrize(
    'template, is_url',
    [
        ('/path/to/zipfile.zip', False),
        ('https://example.com/path/to/zipfile.zip', True),
        ('http://example.com/path/to/zipfile.zip', True),
    ],
)
def test_zipfile_unzip(
    change_dir_main_fixtures, mocker, template, is_url, user_config_data
):
    """Verify zip files correctly handled for different source locations.

    `unzip()` should be called with correct args when `determine_repo_dir()`
    is passed a zipfile, or a URL to a zipfile.
    """
    mock_clone = mocker.patch(
        'tackle.repository.unzip', return_value='fake-repo-tmpl', autospec=True,
    )

    source, mode, settings = update_source_fixtures(
        template,
        abbreviations={},
        clone_to_dir=user_config_data['tackle_dir'],
        checkout=None,
        no_input=True,
        password=None,
    )
    repository.update_source(source=source, mode=mode, settings=settings)

    mock_clone.assert_called_once_with(
        zip_uri=template,
        is_url=is_url,
        clone_to_dir=user_config_data['tackle_dir'],
        no_input=True,
        password=None,
    )

    # assert os.path.isdir(project_dir)
    # assert cleanup
    # assert 'tests/legacy/fixtures/fake-repo-tmpl' == project_dir


@pytest.fixture
def template_url():
    """URL to example Cookiecutter template on GitHub.

    Note: when used, git clone is mocked.
    """
    return 'https://github.com/pytest-dev/cookiecutter-pytest-plugin.git'


def test_repository_url_should_clone(
    change_dir_main_fixtures, mocker, template_url, user_config_data
):
    """Verify repository url triggers clone function.

    `clone()` should be called with correct args when `determine_repo_dir()` is
    passed a repository template url.
    """
    mock_clone = mocker.patch(
        'tackle.repository.clone', return_value='fake-repo-tmpl', autospec=True,
    )

    source, mode, settings = update_source_fixtures(
        template_url,
        abbreviations={},
        clone_to_dir=user_config_data['tackle_dir'],
        checkout=None,
        no_input=True,
    )
    repository.update_source(source=source, mode=mode, settings=settings)

    mock_clone.assert_called_once_with(
        repo_url=template_url,
        checkout=None,
        clone_to_dir=user_config_data['tackle_dir'],
        no_input=True,
    )

    assert os.path.isdir(source.repo_dir)
    assert not source.cleanup
    assert source.context_file == 'cookiecutter.json'


def test_repository_url_with_no_context_file(
    change_dir_main_fixtures, mocker, template_url, user_config_data
):
    """Verify cloned repository without `cookiecutter.json` file raises error."""
    mocker.patch(
        'tackle.repository.clone', return_value='fake-repo-bad', autospec=True,
    )

    with pytest.raises(exceptions.RepositoryNotFound) as err:
        source, mode, settings = update_source_fixtures(
            template_url,
            abbreviations={},
            clone_to_dir=user_config_data['tackle_dir'],
            checkout=None,
            no_input=True,
        )
        repository.update_source(source=source, mode=mode, settings=settings)

    assert str(err.value) == (
        'A valid repository for "{}" could not be found in the following '
        'locations:\n{}'.format(template_url, 'fake-repo-bad')
    )
