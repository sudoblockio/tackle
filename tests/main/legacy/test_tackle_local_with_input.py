"""Test main tackle invocation with user input enabled (mocked)."""
import os

import pytest

import tackle.utils.paths
from tackle import main


@pytest.fixture(scope='function')
def remove_additional_dirs(request, change_dir_main_fixtures):
    """Remove special directories which are created during the tests."""
    yield
    if os.path.isdir('fake-project'):
        tackle.utils.paths.rmtree('fake-project')
    if os.path.isdir('fake-project-input-extra'):
        tackle.utils.paths.rmtree('fake-project-input-extra')


@pytest.mark.usefixtures('clean_system', 'remove_additional_dirs')
def test_tackle_local_with_input(change_dir_main_fixtures):
    """Verify simple tackle run results, without extra_context provided."""
    main.tackle('fake-repo-pre', no_input=True)
    assert os.path.isdir('fake-repo-pre/{{cookiecutter.repo_name}}')
    assert not os.path.isdir('fake-repo-pre/fake-project')
    assert os.path.isdir('fake-project')
    assert os.path.isfile('fake-project/README.rst')
    assert not os.path.exists('fake-project/json/')


@pytest.mark.usefixtures('clean_system', 'remove_additional_dirs')
def test_tackle_input_overwrite_inputs(change_dir_main_fixtures):
    """Verify simple tackle run results, with extra_context provided."""
    # monkeypatch.setattr(
    #     'tackle.utils.prompts.read_user_variable', lambda var, default: default
    # )
    main.tackle(
        'fake-repo-pre',
        no_input=True,
        overwrite_inputs={'repo_name': 'fake-project-input-extra'},
    )
    assert os.path.isdir('fake-project-input-extra')
