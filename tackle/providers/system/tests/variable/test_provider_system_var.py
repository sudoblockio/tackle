# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.variable` module."""
from tackle.main import tackle


def test_provider_system_hook_stat(change_dir):
    """Verify the hook call works properly."""
    output = tackle(no_input=True, context_file='stat.yaml')

    assert output['a_list_remove'] == ['things']
    assert output['map_update'] == {'stuff': {'dogs': 'cats'}, 'foo': 'bar'}
    assert output['map_merge'] == {
        'stuff': {'things': 3, 'dogs': 'cats'},
        'foo': 'bar',
    }
    assert output['loop_merge'][1] == {'stuff': {'things': 1}, 'foo': 'bar'}
    assert output['boolean']


def test_provider_system_hook_var(change_dir):
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


def test_provider_system_hook_var_lists_embed(change_dir):
    """Verify the hook call works properly."""
    output = tackle(no_input=True, context_file='lists.yaml')

    assert output['list_of_lists'] == [[1, 2], [3, 4]]
