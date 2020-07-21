# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.aws.azs` module."""

import os
import yaml
from cookiecutter.main import cookiecutter


def test_embedded_context(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    inner_yaml = os.path.join('stuffs', 'things', 'before.yaml')
    if os.path.exists('after.yaml'):
        os.remove('after.yaml')
    if os.path.exists(inner_yaml):
        os.remove(inner_yaml)

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert context['stuff_nuki']['foo'] == 'bar'
    with open(inner_yaml) as f:
        embedded_yaml = yaml.load(f)

    assert embedded_yaml['foo'] == 'bar'
    assert embedded_yaml['stuff'] == 'Indeed'
    assert embedded_yaml['things'] == 'yes please'

    inner_yaml = os.path.join('stuffs', 'things', 'before.yaml')
    if os.path.exists('after.yaml'):
        os.remove('after.yaml')
    if os.path.exists(inner_yaml):
        os.remove(inner_yaml)
