from tackle import tackle


def test_hook_sort_in_place(change_dir):
    output = tackle('sort-in-place.yaml')
    assert output['a_list'] == ['bar', 'baz', 'foo']
    assert output['b_list'] == ['foo', 'bar', 'baz']
    assert output['sort_in_list'] == ['bar', 'baz', 'foo']


def test_hook_sort_map_key(change_dir):
    output = tackle('sort-map.yaml')
    assert output['sort_a_map'][0]['foo'] == 'bar'


def test_collections_hook_list_key(change_dir):
    output = tackle('list-keys.yaml')
    assert output['list_key_values'] == ['things', 'mo tings']


def test_collections_hook_concatenate(change_dir):
    output = tackle('concatenate.yaml')
    assert output['out'] == ['foo', 'bar', 'stuff', 'things']


def test_collections_hook_distinct(change_dir):
    output = tackle('distinct.yaml')
    for i in output['distincts']:
        assert i in ['stuff', 'foo', 'things']
