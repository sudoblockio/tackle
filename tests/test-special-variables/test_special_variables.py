# -*- coding: utf-8 -*-

"""Tests dict rednering special variables."""
import os
from cookiecutter.main import cookiecutter


def test_special_variables(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert context
