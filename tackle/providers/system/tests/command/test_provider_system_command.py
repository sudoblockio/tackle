# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.command` module."""
import os
import pytest

from tackle.main import tackle

if os.name == 'nt':
    pytest.skip("Skipping when run from windows.", allow_module_level=True)


def test_provider_system_hook_command(change_dir):
    """Verify the hook call works properly."""
    context = tackle('.', no_input=True)

    assert 'tackle.yaml' in context['shell']
    assert 'tackle.yaml' in context['cmd']


def test_provider_system_hook_command_multi_line(change_dir):
    """Verify the hook call works properly."""
    context = tackle('.', context_file='multi-line-cmd.yaml', no_input=True)
    assert 'No such file' not in context['shell']
