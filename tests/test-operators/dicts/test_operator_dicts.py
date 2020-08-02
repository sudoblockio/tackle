# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.block` module."""
import os
from cookiecutter.main import cookiecutter


def _clean_outputs():
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)


def test_operator_dicts(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
    _clean_outputs()
    output = cookiecutter(
        '.', context_file='merge.yaml', no_input=True, output_dir=str(tmpdir)
    )
    assert output

    output = cookiecutter(
        '.', context_file='update.yaml', no_input=True, output_dir=str(tmpdir)
    )
    assert output

    output = cookiecutter(
        '.', context_file='pop.yaml', no_input=True, output_dir=str(tmpdir)
    )
    assert 'stuff' not in output['pop_map']
    assert 'things' not in output['pop_maps']
    _clean_outputs()
