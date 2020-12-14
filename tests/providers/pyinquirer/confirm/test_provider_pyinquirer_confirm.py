# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import pytest
from tackle.main import tackle


@pytest.mark.parametrize("clean_output", ["tackle.record.yaml"], indirect=True)
def test_provider_pyinquirer_confirm_hook(monkeypatch, tmpdir, clean_output):
    """Verify the hook call works successfully."""
    o = tackle('.', no_input=True, output_dir=str(tmpdir), rerun=True,)

    assert 'this' in o
