import sys
import os
import pytest

# from tackle.exceptions import HookCallException

from tackle.main import tackle

if os.name == 'nt':
    pytest.skip("Skipping when run from windows.", allow_module_level=True)


# No idea why this fails - same command...
# def test_provider_system_hook_command(change_dir):
#     context = tackle('list-dir.yaml')
#     assert context['cmd'] == context['cmd_arg']


# TODO: https://github.com/robcxyz/tackle/issues/14
# TODO: https://github.com/robcxyz/tackle/issues/71
@pytest.mark.skipif(
    sys.platform == 'darwin', reason="https://github.com/robcxyz/tackle/issues/71"
)
def test_provider_system_hook_command_multi_line(change_dir):
    output = tackle('multi-line-cmd.yaml')
    assert output['multiline'].startswith('stuff and thing')
    assert output['singleline'].startswith('stuff and thing')


# TODO: https://github.com/robcxyz/tackle/issues/13
# def test_provider_system_hook_interactive_shell(chdir):
#     o = tackle('interactive.yaml')
#     assert o


# def test_provider_system_hook_shell_exit(change_dir):
#     with pytest.raises(FileNotFoundError):
#         tackle('exit.yaml')
#
#
# def test_provider_system_hook_shell_exit_long(change_dir):
#     with pytest.raises(HookCallException):
#         tackle('exit-long.yaml')


def test_provider_system_hook_shell_exit_ignore(change_dir):
    o = tackle('exit-ignore.yaml')
    assert o


def test_provider_system_hook_command_exit_ignore(change_dir):
    o = tackle('exit-ignore.yaml')
    assert o
