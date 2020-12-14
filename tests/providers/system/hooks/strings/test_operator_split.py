# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.stat` module."""
import os
from cookiecutter.main import cookiecutter


def test_provider_system_hook_split(change_dir):
    """Verify the hook call works properly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    output = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert output['a_list'] == [['stuff', 'thing'], ['things', 'stuffs']]
    assert output['a_str'] == ['things', 'stuffs']
    assert output['join_a_str'] == 'things.stuffs'
