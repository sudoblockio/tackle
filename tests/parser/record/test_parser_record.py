# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import oyaml as yaml
from tackle.main import tackle
import pytest


@pytest.mark.parametrize("clean_output", ["tackle.record.yaml"], indirect=True)
def test_parser_record_bool_input(tmpdir, change_dir, clean_output):
    """Verify that when the record flag is set, the output is the ."""
    o = tackle('.', no_input=True, output_dir=str(tmpdir), record=True,)

    with open(clean_output) as f:
        record_output = yaml.load(f)

    assert 'stuff' in o
    assert 'stuff' in record_output


@pytest.mark.parametrize("clean_output", ["record2.yaml"], indirect=True)
def test_parser_record_str_input(tmpdir, change_dir, clean_output):
    """Verify the hook call works successfully."""
    o2 = tackle('.', no_input=True, output_dir=str(tmpdir), record=clean_output,)

    with open(clean_output) as f:
        record_output = yaml.load(f)

    assert 'stuff' in o2
    assert 'stuff' in record_output


@pytest.mark.parametrize("clean_output", ["tackle-other.record.yaml"], indirect=True)
def test_parser_record_str_input_and_different_input(tmpdir, change_dir, clean_output):
    """Verify the hook call works successfully."""
    o2 = tackle(
        '.',
        no_input=True,
        output_dir=str(tmpdir),
        context_file='tackle-other.yaml',
        record=True,
    )

    with open(clean_output) as f:
        record_output = yaml.load(f)

    assert 'stuff' in o2
    assert 'stuff' in record_output


def test_parser_record_cli(tmpdir, change_dir, cli_runner):
    result = cli_runner('.', '--no-input')
    print()
