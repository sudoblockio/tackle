# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from tackle.main import tackle


def test_provider_system_hook_random_string(change_dir):
    """Verify the hook call works properly."""
    output = tackle('.', no_input=True, context_file='nuki.yaml')

    assert len(output['random_hex']) == 8
    assert len(output['random_string']) == 8
