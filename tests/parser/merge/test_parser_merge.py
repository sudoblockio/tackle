import pytest

from tackle import exceptions, tackle


def test_parser_merge_dict():
    """Validate merging a dict into a dict."""
    output = tackle('dict.yaml')

    assert output['resources']['name'] == 'operator'
    assert output['resources']['foo'] == 'foo'


def test_parser_merge_list_value():
    """
    Validate that when in a list, running a hook with a merge overwrites the list.

    Note: this is kind of strong... But what else is it supposed to mean? Don't use
     merge for values...
    """
    output = tackle('list-value.yaml')

    assert output['resources'] == 'foo'


def test_parser_merge_list_loop_value():
    """
    Validate that when in a list, running a hook in a for loop with a merge appends to
     the list.
    """
    output = tackle('list-loop-value.yaml')

    assert len(output['resources']) == 5
    assert output['resources'][2] == 'foo-0'


def test_parser_merge_list_loop_dict():
    """Same as above but with a dict."""
    output = tackle('list-loop-dict.yaml')

    assert len(output['resources']) == 5
    assert output['resources'][2]['foo-0'] == 'foo-0'
    assert output['resources'][3]['foo-1'] == 'foo-1'


def test_parser_merge_dict_loop_dict():
    """
    Validate that when in a dict, running a hook in a for loop with a merge adds new
     keys to the output.
    """
    output = tackle('dict-loop-dict.yaml')

    assert output['resources']['foo-2'] == 'foo-2'
    assert output['resources']['name'] == 'operator'
    assert output['resources']['foo-1'] == 'foo-1'


# def test_parser_merge_list_dict():
#     """Validate when we merge a list into a dict that it overwrites the contents."""
#     output = tackle('list-dict.yaml')
#     # TODO: Determine how to merge twice into a list
#     #  https://github.com/sudoblockio/tackle/issues/163
#     assert output


def test_parser_merge_dict_loop_exception():
    """
    Validate exception that when in a dict, running a hook in a for loop with a merge
     with the hook output being a value.
    """
    with pytest.raises(exceptions.AppendMergeException):
        tackle('dict-loop-exception.yaml')
