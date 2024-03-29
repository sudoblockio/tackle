"""Tests dict input objects for `tackle.providers.system.hooks.variable` module."""
import os
import shutil

import pytest

from tackle.main import tackle


@pytest.fixture()
def clean_outputs():
    """Clean the outputs."""
    yield
    files = ["things.zip", "things"]
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        if os.path.isdir(f):
            shutil.rmtree(f)


def test_provider_system_zip_dir(clean_outputs):
    output = tackle('zip-dir.yaml')

    assert os.path.isfile(output['dir'])


def test_provider_system_zip_file(clean_outputs):
    output = tackle('zip-file.yaml')

    assert os.path.isfile(output['file'])


def test_provider_system_zip_unzip(clean_outputs):
    output = tackle('unzip.yaml')

    assert os.path.isdir(output['dir'])
