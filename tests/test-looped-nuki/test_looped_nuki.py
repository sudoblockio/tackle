# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.aws.azs` module."""

import os
from cookiecutter.main import cookiecutter


def test_looped_nuki(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
    outputs = [x for x in os.listdir('nukis') if x.startswith('output')]
    for o in outputs:
        os.remove(os.path.join('nukis', o))
    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert len(context['a_list_of_strings_nuki']) == 3

    outputs = [x for x in os.listdir('nukis') if x.startswith('output')]
    for o in outputs:
        os.remove(os.path.join('nukis', o))
