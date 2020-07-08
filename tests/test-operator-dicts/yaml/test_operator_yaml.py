# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.checkbox` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_yaml(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter(
        '.', context_file='before.yaml', no_input=True, output_dir=str(tmpdir),
    )

    assert context['things'] == ['stuff', 'things']

    context = cookiecutter(
        '.', context_file='after.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert context['things'] == ['stuff', 'things']
