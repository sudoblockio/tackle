# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.copy` module."""
import os
import shutil
from tackle.main import tackle


def clean_files():
    """Clean the run."""
    files = ['thing.yaml', 'thing2.yaml', 'stuff']
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        if os.path.isdir(f):
            shutil.rmtree(f)


def test_provider_system_hook_file(change_dir):
    """Verify the hook call works properly."""
    clean_files()

    tackle('.', no_input=True)

    assert 'thing.yaml' in os.listdir()
    assert 'stuff' in os.listdir()

    # If the file has been moved properly there should be only one file
    assert len(os.listdir('stuff')) == 3

    clean_files()
