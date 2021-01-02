# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.dicts` module."""
import os
from tackle.main import tackle
import pytest


@pytest.fixture()
def clean_outputs():
    """Clean the output files."""
    yield
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)


def test_provider_system_hook_dicts_merge(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    output = tackle('.', context_file='merge.yaml', no_input=True)
    assert output['merge_map']['stuff'] == 'blah'
    assert len(output['merge_map']) == 3


def test_provider_system_hook_dicts_update(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    output = tackle('.', context_file='update.yaml', no_input=True)
    assert len(output['update_map']['stuff']) == 2


def test_provider_system_hook_dicts_pop(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    output = tackle('.', context_file='pop.yaml', no_input=True)
    assert 'stuff' not in output['pop_map']
    assert 'things' not in output['pop_maps']
