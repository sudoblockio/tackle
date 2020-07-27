# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.checkbox` module."""

import os
import yaml

from cookiecutter.main import cookiecutter


def test_operator_yaml(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    cookiecutter(
        '.', context_file='update.yaml', no_input=True, output_dir=str(tmpdir),
    )

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['stuff'] == {'things': {'cats': 'scratch'}}

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

    os.remove('output.yaml')
    assert output == ['stuff', 'things']

    read = cookiecutter(
        '.', context_file='read.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert read['stuff'] == 'things'


def test_operator_yaml_update_in_place(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    cookiecutter(
        '.', context_file='update_in_place.yaml', no_input=True, output_dir=str(tmpdir),
    )

    with open('output_update_in_place.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['dev']['stuff'] == 'things'
    os.remove('output_update_in_place.yaml')


def test_operator_yaml_merge_in_place(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    cookiecutter(
        '.', context_file='merge_in_place.yaml', no_input=True, output_dir=str(tmpdir),
    )

    with open('output_merge_in_place.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['dev']['stuff'] == 'things'
    os.remove('output_merge_in_place.yaml')
