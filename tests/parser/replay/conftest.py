"""pytest fixtures for testing cookiecutter's replay feature."""
import pytest
import os


@pytest.fixture
def context():
    """Fixture to return a valid context as known from a cookiecutter.json."""
    return {
        'cookiecutter': {
            'email': 'raphael@hackebrot.de',
            'full_name': 'Raphael Pierzina',
            'github_username': 'hackebrot',
            'version': '0.1.0',
        }
    }


@pytest.fixture
def replay_test_dir():
    """Fixture to test directory."""
    return os.path.join(os.path.abspath(os.path.curdir), 'test-replay')


@pytest.fixture
def mock_user_config(mocker):
    """Fixture to mock user config."""
    return mocker.patch('tackle.main.get_settings')
