# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.stat` module."""
import os
from cookiecutter.main import cookiecutter


def test_provider_system_hook_stat(change_dir):
    """Verify the hook call works properly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    output = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert output['a_list_remove'] == ['things']
    assert output['map_update'] == {'stuff': {'dogs': 'cats'}, 'foo': 'bar'}
    assert output['map_merge'] == {
        'stuff': {'things': 3, 'dogs': 'cats'},
        'foo': 'bar',
    }
    assert output['loop_merge'][1] == {'stuff': {'things': 1}, 'foo': 'bar'}
    assert output['boolean']
