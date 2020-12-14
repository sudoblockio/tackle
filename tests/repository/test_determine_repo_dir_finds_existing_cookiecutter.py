"""Tests around detection whether cookiecutter templates are cached locally."""
import os

import pytest

from cookiecutter import repository


@pytest.fixture
def template():
    """Fixture. Return simple string as template name."""
    return 'cookiecutter-pytest-plugin'


@pytest.fixture
def cloned_cookiecutter_path(user_config_data, template):
    """Fixture. Create fake project directory in special user folder."""
    cookiecutters_dir = user_config_data['cookiecutters_dir']

    cloned_template_path = os.path.join(cookiecutters_dir, template)
    os.mkdir(cloned_template_path)

    open(os.path.join(cloned_template_path, 'cookiecutter.json'), 'w')

    return cloned_template_path


def test_should_return_existing_cookiecutter(
    template, cloned_cookiecutter_path, mode, source, settings
):
    """
    Should find folder created by `cloned_cookiecutter_path` and return it.

    This folder is considered like previously cloned project directory.
    """
    mode.no_input = True

    project_dir, context_file, cleanup = repository.update_source(
        source, settings, mode
    )

    assert cloned_cookiecutter_path == project_dir
    assert context_file == 'cookiecutter.json'
    assert not cleanup


def test_sturf(context):
    print(context)
