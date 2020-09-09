# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.block` module."""
import os
from cookiecutter.main import cookiecutter


def test_operator_block(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    output = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert output['stuff'] == 'here'

    output = cookiecutter(
        '.', context_file='embedded_blocks.yaml', no_input=True, output_dir=str(tmpdir),
    )

    assert output['things'] == 'things'

    output = cookiecutter(
        '.', context_file='looped.yaml', no_input=True, output_dir=str(tmpdir),
    )

    assert len(output['blocker']) == 2

    output = cookiecutter(
        '.', context_file='block_nuki.yaml', no_input=True, output_dir=str(tmpdir),
    )

    assert output['things'] == 'things'
