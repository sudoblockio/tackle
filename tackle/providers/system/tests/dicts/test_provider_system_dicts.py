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


def test_provider_system_hook_dicts_merge(change_dir):
    """Verify the hook call works properly."""
    output = tackle('merge.yaml')
    assert output['merge_map']['stuff'] == 'bing'


def test_provider_system_hook_dicts_update(change_dir):
    """Verify the hook call works properly."""
    output = tackle('update.yaml')
    assert output['update_map'] == output['arg']
    assert output['update_map2'] == output['arg2']


def test_provider_system_hook_dicts_pop(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    output = tackle('pop.yaml')
    assert 'stuff' not in output['pop_map']
    assert 'things' not in output['pop_maps']
    assert output['arg_1'] == ['stuff']
    assert 'foo' not in output['arg_2']
    assert 'baz' in output['arg_2']


def test_provider_system_hook_dicts_keys(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    output = tackle('keys.yaml')
    assert output['arg_1'] == ['stuff', 'things']
