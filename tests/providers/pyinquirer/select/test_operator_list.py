# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.list` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_select(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    # TODO: Need to properly test this with pty. Tests don't cover now
    output = cookiecutter(
        '.', context_file='dict_ok.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert output

    output = cookiecutter(
        '.', context_file='string_index.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert output

    output = cookiecutter(
        '.', context_file='dict_index.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert output

    output = cookiecutter(
        '.', context_file='list_ok.yaml', no_input=True, output_dir=str(tmpdir)
    )
    assert output


# class TestOperatorSelect:
#     @pytest.mark.parametrize('clean_operator', [['var1', 'var2']], indirect=True)
#     def thing(self, clean_operator):

# import pytest
#
# @pytest.mark.usefixtures('clean_operator', items=[1,2])
# def test_thing():
#     assert 1 == 1
