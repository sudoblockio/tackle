"""Fixtures for running CLI tests."""

import os
import pytest
from tackle.utils.paths import rmtree
import tackle.utils.paths


@pytest.fixture
def project_dir():
    """Return test project folder name and remove it after the test."""
    yield 'fake-project-templated'

    if os.path.isdir('fake-project-templated'):
        tackle.utils.paths.rmtree('fake-project-templated')


@pytest.fixture(params=['-f', '--overwrite-if-exists'])
def overwrite_cli_flag(request):
    """Pytest fixture return all `overwrite-if-exists` invocation options."""
    return request.param


# @pytest.fixture
# def remove_fake_project_dir(request):
#     """Remove the fake project directory created during the tests."""
#
#     def fin_remove_fake_project_dir():
#         if os.path.isdir('fake-project'):
#             rmtree('fake-project')
#
#     request.addfinalizer(fin_remove_fake_project_dir)


@pytest.fixture
def remove_fake_project_dir(request, change_dir_main_fixtures):
    """Remove the fake project directory created during the tests."""
    if os.path.isdir('fake-project'):
        rmtree('fake-project')
    yield
    if os.path.isdir('fake-project'):
        rmtree('fake-project')
