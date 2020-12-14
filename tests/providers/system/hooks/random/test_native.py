# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from cookiecutter.main import cookiecutter


def test_provider_system_hook_random_string(change_dir):
    """Verify the hook call works properly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    output = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert len(output['random_hex']) == 8
    assert len(output['random_string']) == 8
