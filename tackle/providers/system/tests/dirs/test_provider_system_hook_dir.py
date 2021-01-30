# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.copy` module."""
import os
import shutil
from tackle.main import tackle
import pytest


@pytest.fixture()
def clean_files(change_dir):
    """Clean the run."""
    yield
    files = ['output', os.path.join('output', 'foo')]
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        if os.path.isdir(f):
            shutil.rmtree(f)


def test_provider_system_hook_file(change_dir, clean_files):
    """Verify the hook call works properly."""
    o = tackle('.', no_input=True)

    assert os.path.isdir('output')
    assert os.path.exists(o['join'])
