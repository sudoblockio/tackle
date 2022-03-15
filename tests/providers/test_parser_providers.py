import pytest
import os
from tackle.main import tackle
import subprocess
import sys


@pytest.fixture()
def temporary_uninstall():
    """Fixture to uninstall a package and install it after the test."""

    def f(package):
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

    return f


def test_parser_provider_import_installs_requirements(
    change_curdir_fixtures, temporary_uninstall
):
    """Validate that if a package is missing, that it will be installed and usable."""
    temporary_uninstall('requests')
    tackle('test-install-dep.yaml')


def test_parser_hooks_raises_error_on_unknown_hook_type(change_curdir_fixtures):
    """Verify raising error.

    Verify that the hook parser raises the right error when the hook type is
    not in the providers.
    """
    from tackle.exceptions import UnknownHookTypeException

    with pytest.raises(UnknownHookTypeException):
        tackle('unknown-hook-type.yaml')


def test_parser_provider_hook_add(change_curdir_fixtures):
    """Validate adding providers.

    Validate that you can give a `__provider` key to point to
    additional providers and make them available as a type.
    """
    os.chdir('test-provider')
    o = tackle('context_provider.yaml')
    assert o['things'] == 'bar'


def test_parser_provider_hook_add_list(change_curdir_fixtures):
    """Validate that hooks are imported when called from the same directory."""
    o = tackle('context-provider-list.yaml')
    assert o['things'] == 'bar'
    assert o['stuff'] == 'bar'


def test_providers_local_hooks_dir(chdir_fixture):
    """
    Check that when you call from a child dir that you import the hooks from the dir
     with the file being called.
    """
    chdir_fixture(os.path.join('child', 'dir'))
    o = tackle()
    assert o
