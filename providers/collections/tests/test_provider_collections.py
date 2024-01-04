from tackle import tackle


def test_providers_collections_sort_in_place():
    output = tackle('sort-in-place.yaml')
    assert output['a_list'] == ['bar_a', 'baz_a', 'foo_a']
    assert output['b_list'] == ['foo_b', 'bar_b', 'baz_b']
    assert output['sort_in_list'] == ['bar_b', 'baz_b', 'foo_b']


def test_providers_collections_sort_map_func():
    output = tackle('sort-map-func.yaml')
    assert output['sort_a_map'][0]['foo'] == 'bar'


def test_providers_collections_sort_map_keys():
    output = tackle('sort-map-keys.yaml')
    assert output['sort_a_map'][1]['foo'] == 'bar'


def test_providers_collections_hook_list_key():
    output = tackle('list-keys.yaml')
    assert output['list_key_values'] == ['things', 'mo tings']


def test_providers_collections_hook_concatenate():
    output = tackle('concatenate.yaml')
    assert output['out'] == ['foo', 'bar', 'stuff', 'things']


def test_providers_collections_hook_distinct():
    output = tackle('distinct.yaml')
    for i in output['distincts']:
        assert i in ['stuff', 'foo', 'things']


def test_providers_collections_hook_range():
    o = tackle('range.yaml')
    assert o['forward_1'] == [0, 1, 2]
    assert o['forward_2'] == [1, 2]
    assert o['backward_2'] == [3, 2]
    assert o['forward_3'] == [0, 2, 4]
    assert o['backward_3'] == [6, 4]
