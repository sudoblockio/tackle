# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.variable` module."""
from tackle.main import tackle
import pytest
import os
import shutil


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


def test_provider_system_zip_dir(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    output = tackle('.', no_input=True, context_file='zip-dir.yaml')

    assert os.path.isfile(output['dir'])


def test_provider_system_zip_file(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    output = tackle('.', no_input=True, context_file='zip-file.yaml')

    assert os.path.isfile(output['file'])


def test_provider_system_zip_unzip(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    output = tackle('.', no_input=True, context_file='unzip.yaml')

    assert os.path.isdir(output['dir'])
