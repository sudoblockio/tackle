"""Tests around detection whether cookiecutter templates are cached locally."""
import os

import pytest

from tackle import repository
from tests.repository import update_source_fixtures


@pytest.fixture
def template():
    """Fixture. Return simple string as template name."""
    return 'cookiecutter-pytest-plugin'


@pytest.fixture
def cloned_cookiecutter_path(user_config_data, template):
    """Fixture. Create fake project directory in special user folder."""
    cookiecutters_dir = user_config_data['tackle_dir']

    cloned_template_path = os.path.join(cookiecutters_dir, template)
    os.mkdir(cloned_template_path)

    open(os.path.join(cloned_template_path, 'cookiecutter.json'), 'w')

    return cloned_template_path


def test_should_return_existing_cookiecutter(
    template, cloned_cookiecutter_path, user_config_data, change_dir_main_fixtures
):
    """
    Should find folder created by `cloned_cookiecutter_path` and return it.

    This folder is considered like previously cloned project directory.
    """
    source, mode, settings = update_source_fixtures(
        template=template,
        abbreviations={},
        clone_to_dir=user_config_data['tackle_dir'],
        checkout=None,
        no_input=True,
    )
    repository.update_source(source=source, mode=mode, settings=settings)

    assert cloned_cookiecutter_path == source.repo_dir
    assert source.context_file == 'cookiecutter.json'
    assert not source.cleanup
