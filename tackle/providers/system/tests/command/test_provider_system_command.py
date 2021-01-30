# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.command` module."""
import os
import pytest
from tackle.exceptions import HookCallException

from tackle.main import tackle

if os.name == 'nt':
    pytest.skip("Skipping when run from windows.", allow_module_level=True)


def test_provider_system_hook_command(change_dir):
    """Verify the hook call works properly."""
    context = tackle(no_input=True)

    assert 'tackle.yaml' in context['shell']
    assert 'tackle.yaml' in context['cmd']


def test_provider_system_hook_command_multi_line(change_dir):
    """Verify the hook call works properly."""
    context = tackle(context_file='multi-line-cmd.yaml', no_input=True)
    assert 'No such file' not in context['shell']


def test_provider_system_hook_command_exit(change_dir):
    """Verify the hook call works properly."""
    with pytest.raises(HookCallException):
        tackle(context_file='command-exit.yaml', no_input=True)


def test_provider_system_hook_shell_exit(change_dir):
    """Verify the hook call works properly."""
    with pytest.raises(HookCallException):
        tackle(context_file='shell-exit.yaml', no_input=True)


def test_provider_system_hook_shell_exit_long(change_dir):
    """Verify the hook call works properly."""
    with pytest.raises(HookCallException):
        tackle(context_file='shell-exit-long.yaml', no_input=True)


def test_provider_system_hook_shell_exit_ignore(change_dir):
    """Verify the hook call works properly."""
    o = tackle(context_file='shell-exit-ignore.yaml', no_input=True)
    assert o


def test_provider_system_hook_command_exit_ignore(change_dir):
    """Verify the hook call works properly."""
    o = tackle(context_file='command-exit-ignore.yaml', no_input=True)
    assert o
