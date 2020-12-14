# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from cookiecutter.main import cookiecutter

# from cookiecutter.operator import run_operator, parse_operator


def test_provider_system_hook_command(change_dir):
    """Verify the hook call works properly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))
    print(context)
    assert context


def test_provider_tackle_local(change_dir, tmpdir):
    """Verify the hook call works properly."""
    output = cookiecutter(
        '.', context_file='local.yaml', no_input=True, output_dir=str(tmpdir)
    )
    assert output['shell']['foo'] == 'bing'


def test_provider_tackle_remote(change_dir, tmpdir):
    """Verify the hook call works properly."""
    output = cookiecutter(
        '.', context_file='remote.yaml', no_input=True, output_dir=str(tmpdir)
    )
    assert output['shell']['foo'] == 'bing'
