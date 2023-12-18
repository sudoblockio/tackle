"""Tests for function unzip() from zipfile module."""
import tempfile

import pytest

from tackle.exceptions import InvalidZipRepository
from tackle.utils import zipfiles


def mock_download():
    """Fake download function."""
    with open('fake-repo-tmpl.zip', 'rb') as zf:
        chunk = zf.read(1024)
        while chunk:
            yield chunk
            chunk = zf.read(1024)


def test_unzip_local_file(mocker, tmpdir, cd_fixtures):
    """Local file reference can be unzipped."""
    mock_prompt_and_delete = mocker.patch(
        'tackle.utils.zipfiles.prompt_and_delete',
        return_value=True,
        autospec=True,
    )

    clone_to_dir = tmpdir.mkdir('clone')

    output_dir = zipfiles.unzip(
        'fake-repo-tmpl.zip',
        clone_to_dir=str(clone_to_dir),
    )

    assert output_dir.startswith(tempfile.gettempdir())
    assert not mock_prompt_and_delete.called


def test_unzip_protected_local_file_environment_password(mocker, tmpdir, cd_fixtures):
    """In `unzip()`, the environment can be used to provide a repo password."""
    mock_prompt_and_delete = mocker.patch(
        'tackle.utils.zipfiles.prompt_and_delete',
        return_value=True,
        autospec=True,
    )

    clone_to_dir = tmpdir.mkdir('clone')

    output_dir = zipfiles.unzip(
        'protected-fake-repo-tmpl.zip',
        clone_to_dir=str(clone_to_dir),
        password='sekrit',
    )

    assert output_dir.startswith(tempfile.gettempdir())
    assert not mock_prompt_and_delete.called


def test_unzip_protected_local_file_bad_environment_password(
    mocker, tmpdir, cd_fixtures
):
    """In `unzip()`, an error occurs if the environment has a bad password."""
    mocker.patch(
        'tackle.utils.zipfiles.prompt_and_delete',
        return_value=True,
        autospec=True,
    )

    clone_to_dir = tmpdir.mkdir('clone')

    with pytest.raises(InvalidZipRepository):
        zipfiles.unzip(
            'protected-fake-repo-tmpl.zip',
            clone_to_dir=str(clone_to_dir),
            password='not-the-right-password',
        )


def test_unzip_protected_local_file_user_password_with_noinput(
    mocker, tmpdir, cd_fixtures
):
    """Can't unpack a password-protected repo in no_input mode."""
    mocker.patch(
        'tackle.utils.zipfiles.prompt_and_delete',
        return_value=True,
        autospec=True,
    )

    clone_to_dir = tmpdir.mkdir('clone')

    with pytest.raises(InvalidZipRepository):
        zipfiles.unzip(
            'protected-fake-repo-tmpl.zip',
            clone_to_dir=str(clone_to_dir),
            no_input=True,
        )


def test_unzip_protected_local_file_user_password(mocker, tmpdir, cd_fixtures):
    """A password-protected local file reference can be unzipped."""
    mock_prompt_and_delete = mocker.patch(
        'tackle.utils.zipfiles.prompt_and_delete',
        return_value=True,
        autospec=True,
    )
    mocker.patch('tackle.utils.zipfiles.read_repo_password', return_value='sekrit')

    clone_to_dir = tmpdir.mkdir('clone')

    output_dir = zipfiles.unzip(
        'protected-fake-repo-tmpl.zip',
        clone_to_dir=str(clone_to_dir),
    )

    assert output_dir.startswith(tempfile.gettempdir())
    assert not mock_prompt_and_delete.called


def test_unzip_protected_local_file_user_bad_password(mocker, tmpdir, cd_fixtures):
    """Error in `unzip()`, if user can't provide a valid password."""
    mocker.patch(
        'tackle.utils.zipfiles.prompt_and_delete',
        return_value=True,
        autospec=True,
    )
    mocker.patch(
        'tackle.utils.zipfiles.read_repo_password',
        return_value='not-the-right-password',
    )

    clone_to_dir = tmpdir.mkdir('clone')

    with pytest.raises(InvalidZipRepository):
        zipfiles.unzip(
            'protected-fake-repo-tmpl.zip',
            clone_to_dir=str(clone_to_dir),
        )


def test_empty_zip_file(mocker, tmpdir, cd_fixtures):
    """In `unzip()`, an empty file raises an error."""
    mocker.patch(
        'tackle.utils.zipfiles.prompt_and_delete',
        return_value=True,
        autospec=True,
    )

    clone_to_dir = tmpdir.mkdir('clone')

    with pytest.raises(InvalidZipRepository):
        zipfiles.unzip(
            'empty.zip',
            clone_to_dir=str(clone_to_dir),
        )


def test_non_repo_zip_file(mocker, tmpdir, cd_fixtures):
    """In `unzip()`, a repository must have a top level directory."""
    mocker.patch(
        'tackle.utils.zipfiles.prompt_and_delete',
        return_value=True,
        autospec=True,
    )

    clone_to_dir = tmpdir.mkdir('clone')

    with pytest.raises(InvalidZipRepository):
        zipfiles.unzip(
            'not-a-repo.zip',
            clone_to_dir=str(clone_to_dir),
        )


def test_bad_zip_file(mocker, tmpdir, cd_fixtures):
    """In `unzip()`, a corrupted zip file raises an error."""
    mocker.patch(
        'tackle.utils.zipfiles.prompt_and_delete',
        return_value=True,
        autospec=True,
    )

    clone_to_dir = tmpdir.mkdir('clone')

    with pytest.raises(InvalidZipRepository):
        zipfiles.unzip(
            'bad-zip-file.zip',
            clone_to_dir=str(clone_to_dir),
        )


# TODO: These tests worked until removing requests dependency.
# Requests could be added back later in which case these can be enabled.

# def test_unzip_url(mocker, tmpdir, cd_fixtures):
#     """In `unzip()`, a url will be downloaded and unzipped."""
#     mock_prompt_and_delete = mocker.patch(
#         'tackle.utils.zipfiles.prompt_and_delete',
#         return_value=True,
#         autospec=True,
#     )
#
#     request = mocker.MagicMock()
#     request.iter_content.return_value = mock_download()
#
#     mocker.patch(
#         'tackle.utils.zipfiles.requests.get',
#         return_value=request,
#         autospec=True,
#     )
#
#     clone_to_dir = tmpdir.mkdir('clone')
#
#     output_dir = zipfiles.unzip(
#         'https://example.com/path/to/fake-repo-tmpl.zip',
#         clone_to_dir=str(clone_to_dir),
#     )
#
#     assert output_dir.startswith(tempfile.gettempdir())
#     assert not mock_prompt_and_delete.called


# def test_unzip_url_existing_cache(mocker, tmpdir, cd_fixtures):
#     """Url should be downloaded and unzipped, old zip file will be removed."""
#     mock_prompt_and_delete = mocker.patch(
#         'tackle.utils.zipfiles.prompt_and_delete',
#         return_value=True,
#         autospec=True,
#     )
#
#     request = mocker.MagicMock()
#     request.iter_content.return_value = mock_download()
#
#     mocker.patch(
#         'tackle.utils.zipfiles.requests.get',
#         return_value=request,
#         autospec=True,
#     )
#
#     clone_to_dir = tmpdir.mkdir('clone')
#
#     # Create an existing cache of the zipfiles
#     existing_zip = clone_to_dir.join('fake-repo-tmpl.zip')
#     existing_zip.write('This is an existing zipfiles')
#
#     output_dir = zipfiles.unzip(
#         'https://example.com/path/to/fake-repo-tmpl.zip',
#         clone_to_dir=str(clone_to_dir),
#     )
#
#     assert output_dir.startswith(tempfile.gettempdir())
#     assert mock_prompt_and_delete.call_count == 1


# def test_unzip_url_existing_cache_no_input(mocker, tmpdir, cd_fixtures):
#     """If no_input is provided, the existing file should be removed."""
#     request = mocker.MagicMock()
#     request.iter_content.return_value = mock_download()
#
#     mocker.patch(
#         'tackle.utils.zipfiles.requests.get',
#         return_value=request,
#         autospec=True,
#     )
#
#     clone_to_dir = tmpdir.mkdir('clone')
#
#     # Create an existing cache of the zipfiles
#     existing_zip = clone_to_dir.join('fake-repo-tmpl.zip')
#     existing_zip.write('This is an existing zipfiles')
#
#     output_dir = zipfiles.unzip(
#         'https://example.com/path/to/fake-repo-tmpl.zip',
#         clone_to_dir=str(clone_to_dir),
#         no_input=True,
#     )
#
#     assert output_dir.startswith(tempfile.gettempdir())


# def test_unzip_should_abort_if_no_redownload(mocker, tmpdir, cd_fixtures):
#     """Should exit without cloning anything If no redownload."""
#     mocker.patch(
#         'tackle.utils.zipfiles.prompt_and_delete',
#         side_effect=SystemExit,
#         autospec=True,
#     )
#
#     mock_requests_get = mocker.patch(
#         'tackle.utils.zipfiles.requests.get',
#         autospec=True,
#     )
#
#     clone_to_dir = tmpdir.mkdir('clone')
#
#     # Create an existing cache of the zipfiles
#     existing_zip = clone_to_dir.join('fake-repo-tmpl.zip')
#     existing_zip.write('This is an existing zipfiles')
#
#     zipfiles_url = 'https://example.com/path/to/fake-repo-tmpl.zip'
#
#     with pytest.raises(SystemExit):
#         zipfiles.unzip(zipfiles_url, clone_to_dir=str(clone_to_dir))
#
#     assert not mock_requests_get.called
