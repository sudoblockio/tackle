# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from tackle.main import tackle


def test_provider_system_hook_command(change_dir):
    """Verify the hook call works properly."""
    if os.name == 'nt':
        # Not testing windows
        pass
    else:
        monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

        context = tackle('.', no_input=True, output_dir=str(tmpdir))

        assert 'nuki.yaml' in context['shell']
        assert 'nuki.yaml' in context['cmd']


def test_provider_system_hook_command_multi_line(change_dir):
    """Verify the hook call works properly."""
    if os.name == 'nt':
        # Not testing windows
        pass
    else:
        monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

        context = tackle(
            '.',
            context_file='multi-line-cmd.yaml',
            no_input=True,
            output_dir=str(tmpdir),
        )

        assert context
        # assert '__init__.py' in context['shell']
        # assert '__init__.py' in context['cmd']


base_dir = os.path.dirname(__file__)
context = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'details': {"type": "command", "command": "ls " + base_dir},
    }
}
