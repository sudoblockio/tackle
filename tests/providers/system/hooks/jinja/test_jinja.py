# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from cookiecutter.main import cookiecutter


def test_operator_jinja(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
    if os.path.exists('things.py'):
        os.remove('things.py')

    context = cookiecutter(
        '.', context_file='nuki.yaml', no_input=True, output_dir=str(tmpdir)
    )
    assert context['foo'] == 'bar'
    if os.path.exists('things.py'):
        os.remove('things.py')
