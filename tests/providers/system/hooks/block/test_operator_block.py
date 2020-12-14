# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.block` module."""
import os
from cookiecutter.main import cookiecutter


def test_provider_system_hook_block_(change_dir):
    """Verify the hook call works properly."""

    output = cookiecutter('.', no_input=True)

    assert output['stuff'] == 'here'

    output = cookiecutter('.', context_file='embedded_blocks.yaml', no_input=True,)

    assert output['things'] == 'things'

    output = cookiecutter('.', context_file='looped.yaml', no_input=True,)

    assert len(output['blocker']) == 2

    output = cookiecutter('.', context_file='block_nuki.yaml', no_input=True,)

    assert output['things'] == 'things'
