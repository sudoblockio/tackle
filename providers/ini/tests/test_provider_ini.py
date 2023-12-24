import os

import pytest

from tackle.main import tackle
from tackle.utils.hooks import get_hook


@pytest.fixture()
def clean_outputs():
    """Remove all the files prefixed with output before and after test."""
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)
    yield
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)


def test_provider_ini_read(clean_outputs):
    output = tackle()
    assert os.path.exists('output.ini')
    assert output['read']['section']['stuff'] == 'things'
    assert output['read']['another']['foo'] is None


def test_provider_ini_encode():
    Hook = get_hook('ini_encode')
    output = Hook(data={"Section1": {"keyA": "valueA", "keyB": "valueB"}}).exec()
    assert (
        output
        == """[Section1]
keyA = valueA
keyB = valueB

"""
    )


def test_provider_ini_decode():
    Hook = get_hook('ini_decode')
    output = Hook(
        data="""[Section1]
keyA = valueA
keyB = valueB
"""
    ).exec()
    assert output == {"Section1": {"keyA": "valueA", "keyB": "valueB"}}
