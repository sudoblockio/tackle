import shutil

import pytest
import os
import subprocess
import sys

from tackle.main import tackle
from tackle.settings import settings


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
    try:
        import requests
    except ImportError:
        assert True

    tackle('test-install-dep.yaml')
    import requests  # noqa

    assert requests


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


@pytest.fixture()
def remove_provider():
    """Fixture to remove a provider."""

    def f(provider):
        provider = provider.split('/')
        provider_path = os.path.join(settings.provider_dir, *provider)
        if os.path.exists(provider_path):
            shutil.rmtree(provider_path)

    return f


def test_providers_released(chdir_fixture, remove_provider):
    """
    Check that when we call a released provider, that we only use commits from the
    latest release and not anything that was added after the release. Check the external
     fixture for details.
    """
    remove_provider("robcxyz/tackle-fixture-released")
    o = tackle("robcxyz/tackle-fixture-released")
    assert 'released_added_later' not in o
    assert o['released_hook'] == 'foo'


def test_providers_released_latest(chdir_fixture, remove_provider):
    """
    Check that when we call a released provider, that when we include the latest flag
    we use the latest commit.
    """
    remove_provider("robcxyz/tackle-fixture-released")
    o = tackle(
        "robcxyz/tackle-fixture-released",
        latest=True,
    )
    assert 'released_added_later' in o
    assert o['released_hook'] == 'foo'

    # Then test that when we run the provider again that it uses the latest release.
    o = tackle("robcxyz/tackle-fixture-released")
    assert 'released_added_later' not in o
    assert o['released_hook'] == 'foo'


def test_providers_unreleased_import(chdir_fixture, remove_provider):
    """Check that we can use an unreleased provider."""
    remove_provider("robcxyz/tackle-fixture-unreleased")
    o = tackle("robcxyz/tackle-fixture-unreleased", no_input=True)
    assert o['this'] == 'that'
