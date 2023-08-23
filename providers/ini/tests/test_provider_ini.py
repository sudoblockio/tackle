import os
import pytest
from tackle.main import tackle


@pytest.fixture()
def clean_outputs(change_dir):
    """Remove all the files prefixed with output before and after test."""
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)
    yield
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)


def test_provider_ini_read(change_dir, clean_outputs):
    output = tackle()
    assert os.path.exists('output.ini')
    assert output['read']['section']['stuff'] == 'things'
    assert output['read']['another']['foo'] is None
