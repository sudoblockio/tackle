import os
import sys

import pytest

from tackle.main import tackle

# from tackle.exceptions import HookCallException


if os.name == 'nt':
    pytest.skip("Skipping when run from windows.", allow_module_level=True)


# No idea why this fails - same command...
# def test_provider_system_hook_command():
#     context = tackle('list-dir.yaml')
#     assert context['cmd'] == context['cmd_arg']


# TODO: https://github.com/sudoblockio/tackle/issues/14
# TODO: https://github.com/sudoblockio/tackle/issues/71
@pytest.mark.skipif(
    sys.platform == 'darwin', reason="https://github.com/sudoblockio/tackle/issues/71"
)
def test_provider_system_hook_command_multi_line():
    output = tackle('multi-line-cmd.yaml')
    assert output['multiline'].startswith('stuff and thing')
    assert output['singleline'].startswith('stuff and thing')


# TODO: https://github.com/sudoblockio/tackle/issues/13
# def test_provider_system_hook_interactive_shell(chdir):
#     o = tackle('interactive.yaml')
#     assert o


# def test_provider_system_hook_shell_exit():
#     with pytest.raises(FileNotFoundError):
#         tackle('exit.yaml')
#
#
# def test_provider_system_hook_shell_exit_long():
#     with pytest.raises(HookCallException):
#         tackle('exit-long.yaml')


def test_provider_system_hook_shell_exit_ignore():
    o = tackle('exit-ignore.yaml')
    assert o


def test_provider_system_hook_command_exit_ignore():
    o = tackle('exit-ignore.yaml')
    assert o
