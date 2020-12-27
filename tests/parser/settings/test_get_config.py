"""Collection of tests around loading cookiecutter config."""
import pytest
import os

from yaml.scanner import ScannerError

from tackle import utils
from tackle.exceptions import ConfigDoesNotExistException
from tackle.parser.settings import get_settings


def test_merge_configs():
    """Verify default and user config merged in expected way."""
    default = {
        'cookiecutters_dir': '/home/example/some-path-to-templates',
        'replay_dir': '/home/example/some-path-to-replay-files',
        'default_context': {},
        'abbreviations': {
            'gh': 'https://github.com/{0}.git',
            'gl': 'https://gitlab.com/{0}.git',
            'bb': 'https://bitbucket.org/{0}',
        },
    }

    user_config = {
        'default_context': {
            'full_name': 'Raphael Pierzina',
            'github_username': 'hackebrot',
        },
        'abbreviations': {
            'gl': 'https://gitlab.com/hackebrot/{0}.git',
            'pytest-plugin': 'https://github.com/pytest-dev/pytest-plugin.git',
        },
    }

    expected_config = {
        'cookiecutters_dir': '/home/example/some-path-to-templates',
        'replay_dir': '/home/example/some-path-to-replay-files',
        'default_context': {
            'full_name': 'Raphael Pierzina',
            'github_username': 'hackebrot',
        },
        'abbreviations': {
            'gh': 'https://github.com/{0}.git',
            'gl': 'https://gitlab.com/hackebrot/{0}.git',
            'bb': 'https://bitbucket.org/{0}',
            'pytest-plugin': 'https://github.com/pytest-dev/pytest-plugin.git',
        },
    }

    assert utils.merge_configs(default, user_config) == expected_config


def test_get_config(change_dir):
    """Verify valid config opened and rendered correctly."""
    conf = get_settings(config_file='test-config/valid-config.yaml')
    expected_conf = {
        'tackle_dir': '/home/example/some-path-to-templates',
        'replay_dir': '/home/example/some-path-to-replay-files',
        'default_context': {
            'full_name': 'Firstname Lastname',
            'email': 'firstname.lastname@gmail.com',
            'github_username': 'example',
        },
        'abbreviations': {
            'gh': 'https://github.com/{0}.git',
            'gl': 'https://gitlab.com/{0}.git',
            'bb': 'https://bitbucket.org/{0}',
            'helloworld': 'https://github.com/hackebrot/helloworld',
        },
    }
    assert conf.dict()['abbreviations'] == expected_conf['abbreviations']
    assert conf.dict()['default_context'] == expected_conf['default_context']
    assert conf.dict()['replay_dir'] == expected_conf['replay_dir']


def test_get_config_does_not_exist():
    """Check that `exceptions.ConfigDoesNotExistException` is raised when \
    attempting to get a non-existent config file."""
    expected_error_msg = 'Config file tests/not-exist.yaml does not exist.'
    with pytest.raises(ConfigDoesNotExistException) as exc_info:
        get_settings('tests/not-exist.yaml')
    assert str(exc_info.value) == expected_error_msg


#
def test_invalid_config(change_dir):
    """An invalid config file should raise an `InvalidConfiguration` \
    exception."""
    with pytest.raises(ScannerError):
        get_settings('test-config/invalid-config.yaml')


def test_get_config_with_defaults(change_dir):
    """A config file that overrides 1 of 3 defaults."""
    conf = get_settings('test-config/valid-partial-config.yaml')
    default_cookiecutters_dir = os.path.expanduser('~/.tackle/')
    default_replay_dir = os.path.expanduser('~/.tackle/replay')
    expected_conf = {
        'tackle_dir': default_cookiecutters_dir,
        'replay_dir': default_replay_dir,
        'default_context': {
            'full_name': 'Firstname Lastname',
            'email': 'firstname.lastname@gmail.com',
            'github_username': 'example',
        },
        'abbreviations': {
            'gh': 'https://github.com/{0}.git',
            'gl': 'https://gitlab.com/{0}.git',
            'bb': 'https://bitbucket.org/{0}',
        },
    }
    assert conf.dict()['default_context'] == expected_conf['default_context']
    assert conf.dict()['abbreviations'] == expected_conf['abbreviations']
    assert conf.dict()['replay_dir'] == expected_conf['replay_dir']
