"""pytest fixtures which are globally available throughout the suite."""
import pytest
import os
import shutil

from tackle.settings import settings


@pytest.fixture()
def tmp_move_tackle_dir():
    """Fixture to temporarily move tackle dir where providers are stored."""
    if os.path.isdir(settings.tackle_dir):
        shutil.move(settings.tackle_dir, settings.tackle_dir + '.tmp')
    yield
    shutil.move(settings.tackle_dir + '.tmp', settings.tackle_dir)
