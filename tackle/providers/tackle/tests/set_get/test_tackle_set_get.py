"""test for set, get, and delete hooks."""
from tackle import tackle


def test_provider_tackle_set(change_dir):
    """Check that we can set keys."""
    output = tackle('set.yaml')
    assert output['one'][0]['that']['stuff'] == 'more things'
    assert output['two'][0]['that']['stuff'] == 'more things'
    assert output['three'][0]['that']['stuff'] == 'more things'


def test_provider_tackle_get(change_dir):
    """Check that we can get keys."""
    output = tackle('get.yaml')
    assert output['getter_list'] == 'things'
    assert output['getter_str'] == 'things'
    assert output['getter_str_sep'] == 'things'


def test_provider_tackle_delete(change_dir):
    """Check that we can delete keys."""
    output = tackle('delete.yaml')
    assert output['one'][0]['that'] == {}
    assert output['two'][0]['that'] == {}
    assert output['three'][0]['that'] == {}
