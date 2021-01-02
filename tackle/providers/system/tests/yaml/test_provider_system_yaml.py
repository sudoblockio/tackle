# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.yaml` module."""
import os
import yaml
import pytest
from tackle.main import tackle


@pytest.fixture()
def clean_outputs(change_dir):
    """Remove all the files prefixed with output before and after test."""
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)
    yield
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)


def test_provider_system_hook_yaml_update(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    tackle('.', context_file='update.yaml', no_input=True)

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['stuff'] == {'things': {'cats': 'scratch'}}


def test_provider_system_hook_yaml_remove_str(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    tackle('.', context_file='remove_str.yaml', no_input=True)

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output == ['stuff', 'things']


def test_provider_system_hook_yaml_remove_list(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    tackle('.', context_file='remove_list.yaml', no_input=True)

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output == ['stuff', 'things']


def test_provider_system_hook_yaml_read(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    read = tackle('.', context_file='read.yaml', no_input=True)

    assert read['stuff'] == 'things'


def test_provider_system_hook_yaml_filter(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    output = tackle('.', context_file='filter.yaml', no_input=True)

    assert 'stuff' not in output['things']


def test_provider_system_hook_yaml_update_in_place(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    tackle('.', context_file='update_in_place.yaml', no_input=True)

    with open('output_update_in_place.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['dev']['stuff'] == 'things'


def test_provider_system_hook_yaml_merge_in_place(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    tackle('.', context_file='merge_in_place.yaml', no_input=True)

    with open('output_merge_in_place.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['dev']['stuff'] == 'things'


def test_provider_system_hook_yaml_append(change_dir, clean_outputs):
    """Verify the hook call works properly."""
    output = tackle('.', context_file='append.yaml', no_input=True)
    assert output['append_dict'] == {'things': ['dogs', 'cats', 'bar', 'baz']}
