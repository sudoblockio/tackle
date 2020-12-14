# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.checkbox` module."""

import os
import yaml

from tackle.main import tackle


def _clean_outputs():
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)


def test_provider_system_hook_yaml(change_dir):
    """Verify the hook call works properly."""
    _clean_outputs()

    tackle(
        '.', context_file='update.yaml', no_input=True,
    )

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['stuff'] == {'things': {'cats': 'scratch'}}

    tackle('.', context_file='remove_str.yaml', no_input=True)

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output == ['stuff', 'things']

    _clean_outputs()

    tackle('.', context_file='remove_list.yaml', no_input=True)

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    _clean_outputs()
    assert output == ['stuff', 'things']

    read = tackle('.', context_file='read.yaml', no_input=True)

    assert read['stuff'] == 'things'

    output = tackle('.', context_file='filter.yaml', no_input=True)

    assert 'stuff' not in output['things']


def test_provider_system_hook_yaml_update_in_place(change_dir):
    """Verify the hook call works properly."""
    _clean_outputs()

    tackle(
        '.', context_file='update_in_place.yaml', no_input=True,
    )

    with open('output_update_in_place.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['dev']['stuff'] == 'things'
    _clean_outputs()


def test_provider_system_hook_yaml_merge_in_place(change_dir):
    """Verify the hook call works properly."""
    _clean_outputs()

    tackle(
        '.', context_file='merge_in_place.yaml', no_input=True,
    )

    with open('output_merge_in_place.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['dev']['stuff'] == 'things'
    _clean_outputs()


def test_provider_system_hook_yaml_append(change_dir):
    """Verify the hook call works properly."""
    _clean_outputs()
    output = tackle('.', context_file='append.yaml', no_input=True,)
    _clean_outputs()
    assert output['append_dict'] == {'things': ['dogs', 'cats', 'bar', 'baz']}
