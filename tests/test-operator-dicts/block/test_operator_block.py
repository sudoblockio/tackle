# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.block` module."""
import os
from cookiecutter.main import cookiecutter


def test_operator_block(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert context['stuff'] == 'here'

    context = cookiecutter(
        '.',
        context_key='nuki',
        context_file='embedded_blocks.yaml',
        no_input=True,
        output_dir=str(tmpdir),
    )

    assert context['things'] == 'things'
