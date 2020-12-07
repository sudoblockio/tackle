# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from cookiecutter.main import cookiecutter


def test_operator_command(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    if os.name == 'nt':
        # Not testing windows
        pass
    else:
        monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

        context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

        assert 'nuki.yaml' in context['shell']
        assert 'nuki.yaml' in context['cmd']


def test_operator_command_multi_line(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    if os.name == 'nt':
        # Not testing windows
        pass
    else:
        monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

        context = cookiecutter(
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
