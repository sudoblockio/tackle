# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.block` module."""
import os
from tackle.main import tackle


def _clean_outputs():
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)


def test_provider_system_hook_dicts(change_dir):
    """Verify the hook call works properly."""
    _clean_outputs()
    # output = cookiecutter(
    #     '.', context_file='merge.yaml', no_input=True
    # )
    # assert output
    #
    # output = cookiecutter(
    #     '.', context_file='update.yaml', no_input=True
    # )
    # assert output

    output = tackle('.', context_file='pop.yaml', no_input=True)
    assert 'stuff' not in output['pop_map']
    assert 'things' not in output['pop_maps']
    _clean_outputs()
