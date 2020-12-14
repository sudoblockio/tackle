# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import pytest
from cookiecutter.main import cookiecutter


@pytest.mark.parametrize("clean_output", ["tackle.record.yaml"], indirect=True)
def test_provider_toml_hook(monkeypatch, tmpdir, clean_output):
    """Verify the hook call works successfully."""
    o = cookiecutter('.', no_input=True, output_dir=str(tmpdir), rerun=True,)

    assert 'foo' in o
