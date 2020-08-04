# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.block` module."""
import os
import shutil
from cookiecutter.main import cookiecutter


def clean_files():
    """Clean the run."""
    files = ['thing.yaml', 'thing2.yaml', 'stuff']
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        if os.path.isdir(f):
            shutil.rmtree(f)


def test_operator_file(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
    clean_files()

    cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert 'thing.yaml' in os.listdir()
    assert 'stuff' in os.listdir()

    # If the file has been moved properly there should be only one file
    assert len(os.listdir('stuff')) == 3

    clean_files()
