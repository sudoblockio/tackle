# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.parser.providers` module."""
import pytest
from cookiecutter.main import cookiecutter
import subprocess
import sys


@pytest.fixture()
def temporary_uninstall(package='boto3'):
    """Fixture to uninstall a package and install it after the test."""
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "uninstall",
            "--quiet",
            "--disable-pip-version-check",
            "-y",
            package,
        ]
    )
    yield
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "--disable-pip-version-check",
            package,
        ]
    )


def test_parser_provider_import_installs_requirements(
    change_dir_fixture, temporary_uninstall
):
    """Validate that if a package is missing, that it will be installed and usable."""
    cookiecutter('.', context_file='regions.yaml')


def test_parser_hooks_raises_error_on_unknown_hook_type(change_dir_fixture):
    """Verify raising error.

    Verify that the hook parser raises the right error when the hook type is
    not in the providers.
    """
    from cookiecutter.exceptions import UnknownHookTypeException

    with pytest.raises(UnknownHookTypeException):
        cookiecutter('.', context_file='unknown-hook-type.yaml')


def test_parser_provider_hook_add_raise_error(change_dir_fixture):
    """Make sure when hook type is unkown that a validation error is raised."""
    from pydantic.error_wrappers import ValidationError

    with pytest.raises(ValidationError):
        cookiecutter('.', context_file='bad-hook-input.yaml')


def test_parser_provider_hook_add(change_dir_fixture):
    """Validate adding providers.

    Validate that you can give a `__provider` key to point to
    additional providers and make them available as a type.
    """
    o = cookiecutter('.', context_file='context_provider.yaml')
    assert o['things'] == 'bar'


def test_parser_provider_hook_add_list(change_dir_fixture):
    """Validate adding providers.

    Validate that you can give multiple `__provider` keys to point to
    additional providers and make them available as a types.
    """
    o = cookiecutter('.', context_file='context_provider_2.yaml')
    assert o['things'] == 'bar'
    assert o['stuff'] == 'bar'
