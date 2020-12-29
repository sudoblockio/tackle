# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import pytest
from tackle.main import tackle


@pytest.mark.parametrize("clean_output", ["tackle.record.yaml"], indirect=True)
def test_parser_rerun(change_dir, clean_output):
    """Verify the hook call works successfully."""
    o = tackle('.', no_input=True, rerun=True)

    assert 'foo' in o

    # without no_output means the run is using the override
    o = tackle('.', rerun=clean_output)

    assert o['foo'] == ['bar', 'bax', 'bin']
