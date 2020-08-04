# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.checkbox` module."""

import os
import yaml

from cookiecutter.main import cookiecutter


def _clean_outputs():
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)


def test_operator_yaml(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
    _clean_outputs()

    cookiecutter(
        '.', context_file='update.yaml', no_input=True, output_dir=str(tmpdir),
    )

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['stuff'] == {'things': {'cats': 'scratch'}}

    cookiecutter(
        '.', context_file='remove_str.yaml', no_input=True, output_dir=str(tmpdir)
    )

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output == ['stuff', 'things']

    _clean_outputs()

    cookiecutter(
        '.', context_file='remove_list.yaml', no_input=True, output_dir=str(tmpdir)
    )

    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    _clean_outputs()
    assert output == ['stuff', 'things']

    read = cookiecutter(
        '.', context_file='read.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert read['stuff'] == 'things'

    output = cookiecutter(
        '.', context_file='filter.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert 'stuff' not in output['things']


def test_operator_yaml_update_in_place(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
    _clean_outputs()

    cookiecutter(
        '.', context_file='update_in_place.yaml', no_input=True, output_dir=str(tmpdir),
    )

    with open('output_update_in_place.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['dev']['stuff'] == 'things'
    _clean_outputs()


def test_operator_yaml_merge_in_place(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
    _clean_outputs()

    cookiecutter(
        '.', context_file='merge_in_place.yaml', no_input=True, output_dir=str(tmpdir),
    )

    with open('output_merge_in_place.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['dev']['stuff'] == 'things'
    _clean_outputs()


def test_operator_yaml_append(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    _clean_outputs()
    output = cookiecutter(
        '.', context_file='append.yaml', no_input=True, output_dir=str(tmpdir),
    )
    _clean_outputs()
    assert output['append_dict'] == {'things': ['dogs', 'cats', 'bar', 'baz']}
