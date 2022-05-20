from tackle import tackle


def test_hook_sort_in_place(change_dir):
    output = tackle('sort-in-place.yaml')
    assert output['a_list'] == ['bar', 'baz', 'foo']
    assert output['b_list'] == ['foo', 'bar', 'baz']
    assert output['sort_in_list'] == ['bar', 'baz', 'foo']
