# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
from cookiecutter.main import cookiecutter


# import pytest
# @pytest.mark.parametrize("load_yaml", ["tackle.yaml", "tackle2.yaml"], indirect=True)
def test_parser_contexts_overwrite_inputs(tmpdir, change_dir):
    """Verify the hook call works successfully."""
    overwrite_inputs = {'stuff': 'dingdongs'}

    o = cookiecutter(
        '.',
        no_input=True,
        output_dir=str(tmpdir),
        overwrite_inputs=overwrite_inputs,
        context_file='tackle.yaml',
    )
    assert o['stuff'] == 'dingdongs'
