"""pytest fixtures which are globally available throughout the suite."""
import pytest
import os
import shutil

from tackle.settings import settings


@pytest.fixture(scope="function")
def change_dir(request):
    """Change to the current directory of the test."""
    os.chdir(request.fspath.dirname)


@pytest.fixture(scope='function')
def change_curdir_fixtures(request):
    """Change to the fixtures dir in the current directory of the test."""
    os.chdir(os.path.join(request.fspath.dirname, 'fixtures'))


@pytest.fixture(scope='function')
def change_dir_base(monkeypatch):
    """Change to the current directory."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))


@pytest.fixture(scope='function')
def chdir(request):
    """Change to a directory based on an argument within the scope of the test."""

    def f(dir):
        os.chdir(os.path.join(request.fspath.dirname, dir))

    return f


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
