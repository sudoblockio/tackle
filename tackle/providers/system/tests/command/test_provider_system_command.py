"""Tests dict input objects for `tackle.providers.system.hooks.command` module."""
import os
import pytest
from tackle.exceptions import HookCallException

from tackle.main import tackle

if os.name == 'nt':
    pytest.skip("Skipping when run from windows.", allow_module_level=True)


def test_provider_system_hook_command(change_dir):
    """Verify the hook call works properly."""
    fixture = 'list-dir.yaml'
    context = tackle(fixture)
    # assert fixture in context['cmd']
    # assert context['shell']
    assert context['cmd'] == context['cmd_arg']


def test_provider_system_hook_command_multi_line(change_dir):
    """Verify the hook call works properly."""
    context = tackle('multi-line-cmd.yaml')
    assert 'No such file' not in context['shell']


def test_provider_system_hook_command_exit(change_dir):
    """Verify the hook call works properly."""
    with pytest.raises(HookCallException):
        tackle('command-exit.yaml')


def test_provider_system_hook_shell_exit(change_dir):
    """Verify the hook call works properly."""
    with pytest.raises(HookCallException):
        tackle('shell-exit.yaml')


def test_provider_system_hook_shell_exit_long(change_dir):
    """Verify the hook call works properly."""
    with pytest.raises(HookCallException):
        tackle('shell-exit-long.yaml')


def test_provider_system_hook_shell_exit_ignore(change_dir):
    """Verify the hook call works properly."""
    o = tackle('shell-exit-ignore.yaml')
    assert o


def test_provider_system_hook_command_exit_ignore(change_dir):
    """Verify the hook call works properly."""
    o = tackle('command-exit-ignore.yaml')
    assert o
