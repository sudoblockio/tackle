# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.checkbox` module."""

import os
import yaml

from cookiecutter.main import cookiecutter


def test_operator_yaml(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter(
        '.', context_file='before.yaml', no_input=True, output_dir=str(tmpdir),
    )

    assert context['things'] == ['stuff', 'things']

    cookiecutter(
        '.', context_file='remove_str.yaml', no_input=True, output_dir=str(tmpdir)
    )

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output == ['stuff', 'things']

    os.remove('output.yaml')

    cookiecutter(
        '.', context_file='remove_list.yaml', no_input=True, output_dir=str(tmpdir)
    )

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output == ['stuff', 'things']
    os.remove('output.yaml')
