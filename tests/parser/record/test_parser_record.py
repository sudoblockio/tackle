# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import json
from cookiecutter.main import cookiecutter


# @pytest.mark.parametrize("input", ["tackle.yaml"], indirect=True)
def test_parser_record(tmpdir, change_dir):
    """Verify the hook call works successfully."""
    o = cookiecutter(
        '.',
        no_input=True,
        output_dir=str(tmpdir),
        record=True,
        context_file='tackle.yaml',
    )

    with open('record.json') as f:
        record_output = json.load(f)

    assert 'stuff' in o
    assert 'stuff' in record_output

    o = cookiecutter(
        '.',
        no_input=True,
        output_dir=str(tmpdir),
        record='record2.json',
        context_file='tackle.yaml',
    )

    print()
