# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.variable` module."""
from tackle.main import tackle


def test_provider_system_hook_stat(change_dir):
    """Verify the hook call works properly."""
    output = tackle('.', no_input=True, context_file='tackle.yaml')

    assert output['a_list_remove'] == ['things']
    assert output['map_update'] == {'stuff': {'dogs': 'cats'}, 'foo': 'bar'}
    assert output['map_merge'] == {
        'stuff': {'things': 3, 'dogs': 'cats'},
        'foo': 'bar',
    }
    assert output['loop_merge'][1] == {'stuff': {'things': 1}, 'foo': 'bar'}
    assert output['boolean']
