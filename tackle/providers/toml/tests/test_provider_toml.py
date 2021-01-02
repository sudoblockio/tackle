# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.toml.hooks.toml` module."""
import pytest
import os
from tackle.main import tackle


def test_provider_toml_hook_read(change_dir):
    """Verify the hook call works successfully."""
    o = tackle('.', context_file='read.yaml', no_input=True)
    assert 'owner' in o['read'].keys()


@pytest.fixture()
def clean_toml():
    """Remove outputs."""
    yield
    if os.path.exists('writing.toml'):
        os.remove('writing.toml')


def test_provider_toml_hook_write(change_dir, clean_toml):
    """Verify the hook call works successfully."""
    tackle('.', context_file='write.yaml', no_input=True)
    assert os.path.exists('writing.toml')
