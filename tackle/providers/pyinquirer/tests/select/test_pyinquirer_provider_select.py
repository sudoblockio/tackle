"""Tests dict input objects for `tackle.providers.pyinquirer.hooks.select` module."""

import os
from tackle.main import tackle


def test_provider_select(monkeypatch):
    """Verify the hook call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    # TODO: Need to properly test this with pty. Tests don't cover now
    output = tackle('dict_ok.yaml', no_input=True)
    assert output

    output = tackle('string_index.yaml', no_input=True)
    assert output

    output = tackle('dict_index.yaml', no_input=True)
    assert output

    output = tackle('list_ok.yaml', no_input=True)
    assert output
