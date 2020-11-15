# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import pytest
from cookiecutter.main import cookiecutter


@pytest.mark.parametrize("clean_output", ["tackle.record.yaml"], indirect=True)
def test_parser_rerun(monkeypatch, tmpdir, clean_output):
    """Verify the hook call works successfully."""
    o = cookiecutter('.', no_input=True, output_dir=str(tmpdir), rerun=True,)

    assert 'foo' in o

    # without no_output means the run is using the override
    o = cookiecutter('.', output_dir=str(tmpdir), rerun=clean_output,)

    assert 'foo' in o
