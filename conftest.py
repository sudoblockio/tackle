"""Global pytest fixtures."""
import pytest
import os
import sys

from tackle.factory import new_context
from tackle.imports import import_native_providers
from tackle.context import Source


@pytest.fixture(scope='function', autouse=True)
def cd_cwd(request):
    """Change to current directory - default for all tests."""
    os.chdir(request.fspath.dirname)


@pytest.fixture(scope='function')
def cd(request):
    """Change to a local directory from a test, usually a fixtures dir."""

    def f(path: str | list):
        if isinstance(path, list):
            path = os.path.join(*path)
        os.chdir(os.path.join(request.fspath.dirname, path))

    return f


@pytest.fixture(scope='function')
def cd_fixtures(cd):
    """Change to current directories fixtures."""
    cd('fixtures')


@pytest.fixture(scope='function')
def base_dir():
    """Path to base of repo."""
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='function')
def base_hooks_dir(base_dir):
    """Path to base of repo."""
    return os.path.join(base_dir, '.hooks')


@pytest.fixture(scope='function')
def cd_base_dir(monkeypatch, base_dir):
    """Change to the current directory."""
    monkeypatch.chdir(base_dir)


@pytest.fixture()
def context(mocker):
    """An empty context - no source."""
    mocker.patch(
        'tackle.factory.new_source',
        return_value=Source(),
        autospec=True,
    )
    return new_context()


@pytest.fixture(scope='session', autouse=True)
def patch_native_provider_import(session_mocker):
    """
    Importing the native providers is expensive and needs to be done on startup so to
     avoid this we patch it and auto-use the value which is always the same.
    """
    mock = session_mocker.patch(
        'tackle.factory.import_native_providers',
        return_value=import_native_providers(),
    )
    yield mock


def pytest_addoption(parser):
    parser.addoption(
        "--skip-slow", action="store_true", default=False, help="skip slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--skip-slow"):
        skip_slow = pytest.mark.skip(reason="skipped slow test")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


@pytest.fixture
def skip_if_not_linux():
    if not sys.platform.startswith("linux"):
        return pytest.mark.skip(reason="This test runs only on Linux")
