# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import oyaml as yaml
from tackle.main import tackle
import pytest
import os


@pytest.fixture()
def clean_outputs():
    """Clean outputs."""
    yield
    outputs = ["tackle-other.record.yaml", "tackle.record.yaml", "record2.yaml"]
    for o in outputs:
        if os.path.isfile(o):
            os.remove(o)


def test_parser_record_bool_input(change_dir, clean_outputs):
    """Verify that when the record flag is set, the output is the ."""
    o = tackle(
        no_input=True,
        record=True,
    )

    with open("tackle.record.yaml") as f:
        record_output = yaml.safe_load(f)

    assert 'stuff' in o
    assert 'stuff' in record_output


def test_parser_record_str_input(change_dir, clean_outputs):
    """Verify the hook call works successfully."""
    o2 = tackle(
        '.',
        no_input=True,
        record="record2.yaml",
    )

    with open("record2.yaml") as f:
        record_output = yaml.safe_load(f)

    assert 'stuff' in o2
    assert 'stuff' in record_output


# @pytest.mark.parametrize("clean_output", ["tackle-other.record.yaml"], indirect=True)
# def test_parser_record_str_input_and_different_input(change_dir, clean_output):
#     """Verify the hook call works successfully."""
#     o2 = tackle(
#         '.',
#         no_input=True,
#         context_file='tackle-other.yaml',
#         record=True,
#     )
#
#     with open(clean_output) as f:
#         record_output = yaml.load(f)
#
#     assert 'stuff' in o2
#     assert 'stuff' in record_output
#
#
# @pytest.mark.parametrize("clean_output", ["tackle-other.record.yaml"], indirect=True)


def test_parser_record_str_input_and_different_input(change_dir, clean_outputs):
    """Verify that ."""
    o1 = tackle(
        '.',
        no_input=True,
        context_file='tackle-other.yaml',
        record=True,
    )

    out_file = "tackle-other.record.yaml"

    with open(out_file) as f:
        record_output = yaml.safe_load(f)

    assert 'stuff' in o1
    assert 'stuff' in record_output

    o2 = tackle(
        '.',
        context_file='tackle-other.yaml',
        overwrite_inputs=out_file,
    )
    assert o2['blah'] == 'stuff'


# TODO
# def test_parser_record_cli(tmpdir, change_dir, cli_runner):
#     """Make sure the record functionality works."""
#     cli_runner('.', '--no-input')
