"""Tests dict input objects for `tackle.providers.system.hooks.copy` module."""
import os
import shutil

import pytest

from tackle.main import tackle


@pytest.fixture()
def clean_files():
    """Clean the run."""
    yield
    files = ['output', os.path.join('output', 'foo')]
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        if os.path.isdir(f):
            shutil.rmtree(f)


def test_provider_system_hook_file(clean_files):
    o = tackle('tackle.yaml')
    assert os.path.isdir('output')
    assert os.path.exists(o['join'])


def test_provider_system_hook_file_args(clean_files):
    o = tackle('tackle.yaml')
    assert os.path.isdir('output')
    assert os.path.exists(o['join'])
