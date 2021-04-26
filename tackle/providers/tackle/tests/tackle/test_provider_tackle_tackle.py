# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.tackle.hooks.tackle` module."""
from tackle.main import tackle

import pytest
import shutil


@pytest.fixture()
def clean_outputs():
    """Remove the outputs dir."""
    yield
    shutil.rmtree('output')


def test_provider_system_hook_tackle(change_dir):
    """Verify the hook call works properly."""
    # TODO Build example repo
    context = tackle(context_file='tackle.yaml', no_input=True)
    assert context


def test_provider_tackle_local(change_dir):
    """Verify the hook call works properly."""
    output = tackle(context_file='local.yaml', no_input=True)
    assert output['shell']['foo'] == 'bing'


def test_provider_tackle_remote(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    output = tackle('remote.yaml', no_input=True)
    # assert output['shell']['foo'] == 'bing'
    assert output
