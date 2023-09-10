"""
pytest fixtures which are globally available in both `tests` and tests within
`tackle/providers/<provider>/tests`.
"""
import pytest
import os
import shutil
import tempfile

from tackle.settings import settings
from tackle.factory import new_context
from tackle.imports import import_native_providers
from tackle.models import Context


@pytest.fixture(scope="function")
def change_dir(request):
    """Change to the current directory of the test."""
    os.chdir(request.fspath.dirname)


@pytest.fixture(scope='function')
def change_curdir_fixtures(request):
    """Change to the fixtures dir in the current directory of the test."""
    os.chdir(os.path.join(request.fspath.dirname, 'fixtures'))


@pytest.fixture(scope='function')
def base_dir():
    """Path to base of repo."""
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='function')
def base_hooks_dir(base_dir):
    """Path to base of repo."""
    return os.path.join(base_dir, '.hooks')


@pytest.fixture(scope='function')
def change_base_dir(monkeypatch, base_dir):
    """Change to the current directory."""
    monkeypatch.chdir(base_dir)


@pytest.fixture(scope='function')
def chdir(request):
    """Change to a directory based on an argument within the scope of the test."""

    def f(dir):
        os.chdir(os.path.join(request.fspath.dirname, dir))

    return f


@pytest.fixture(scope='function')
def run_in_temp_dir(chdir):
    temp_dir = tempfile.mkdtemp()
    chdir(temp_dir)


@pytest.fixture(scope='function')
def chdir_fixture(request):
    """Change to a directory based on an argument within the scope of the test."""

    def f(dir):
        os.chdir(os.path.join(request.fspath.dirname, 'fixtures', dir))

    return f


@pytest.fixture()
def tmp_move_tackle_dir():
    """Fixture to temporarily move tackle dir where providers are stored."""
    if os.path.isdir(settings.tackle_dir):
        shutil.move(settings.tackle_dir, settings.tackle_dir + '.tmp')
    yield
    shutil.move(settings.tackle_dir + '.tmp', settings.tackle_dir)


@pytest.fixture(scope='session')
def context():
    return new_context()


@pytest.fixture(scope='session', autouse=True)
def patch_native_provider_import(session_mocker):
    """
    Importing the native providers is expensive and needs to be done on startup so to
     avoid this we patch it and auto-use the value which is always the same.
    """
    session_mocker.patch(
        'tackle.factory.import_native_providers',
        return_value=import_native_providers(Context()),
    )

@pytest.fixture(scope='function')
def cd(request):
    """Change to a local directory from a test, usually a fixtures dir."""

    def f(path: str | list):
        if isinstance(path, list):
            path = os.path.join(*path)
        os.chdir(os.path.join(request.fspath.dirname, path))

    return f
