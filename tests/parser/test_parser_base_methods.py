import pytest
from ruamel.yaml import YAML
from tackle import tackle
from tackle import exceptions


def test_parser_methods_merge(change_curdir_fixtures):
    """Verify we can run tackle against a fixture and merge it up to equal the same."""
    yaml = YAML()
    with open('petstore.yaml') as f:
        expected_output = yaml.load(f)

    output = tackle('merge-petstore-compact.yaml')
    assert output == expected_output


@pytest.fixture()
def fixture_dir(chdir):
    chdir("base-method-fixtures")


def test_parser_methods_merge_dict(fixture_dir):
    """Validate merging a dict into a dict."""
    output = tackle('merge-dict.yaml')
    assert output['resources']['name'] == 'operator'
    assert output['resources']['foo'] == 'foo'


def test_parser_methods_merge_list_value(fixture_dir):
    """Validate that when in a list, running a hook with a merge overwrites the list."""
    # Note: this is kind of strong... But what else is it supposed to mean? Don't use
    # merge for values...
    output = tackle('merge-list-value.yaml')
    assert output['resources'] == 'foo'


def test_parser_methods_merge_list_loop_value(fixture_dir):
    """
    Validate that when in a list, running a hook in a for loop with a merge appends to
     the list.
    """
    output = tackle('merge-list-loop-value.yaml')
    assert len(output['resources']) == 5
    assert output['resources'][2] == 'foo-0'


def test_parser_methods_merge_list_loop_dict(fixture_dir):
    """Same as above but with a dict."""
    output = tackle('merge-list-loop-dict.yaml')
    assert len(output['resources']) == 5
    assert output['resources'][2]['foo-0'] == 'foo-0'
    assert output['resources'][3]['foo-1'] == 'foo-1'


def test_parser_methods_merge_dict_loop_dict(fixture_dir):
    """
    Validate that when in a dict, running a hook in a for loop with a merge adds new
     keys to the output.
    """
    output = tackle('merge-dict-loop-dict.yaml')
    assert output['resources']['foo-2'] == 'foo-2'
    assert output['resources']['name'] == 'operator'
    assert output['resources']['foo-1'] == 'foo-1'


def test_parser_methods_merge_dict_loop_exception(fixture_dir):
    """
    Validate exception that when in a dict, running a hook in a for loop with a merge
     with the hook output being a value.
    """
    with pytest.raises(exceptions.AppendMergeException):
        tackle('merge-dict-loop-exception.yaml')


# def test_parser_methods_merge_list_dict(fixture_dir):
#     """Validate when we merge a list into a dict that it overwrites the contents."""
#     output = tackle('merge-list-dict.yaml')
#     # TODO: Determine how to merge twice into a list
#     #  https://github.com/sudoblockio/tackle/issues/163
#     assert output


def test_parser_methods_try(fixture_dir):
    """Use try which should not have any output"""
    output = tackle('method-try.yaml')
    assert output == {}


def test_parser_methods_except(fixture_dir):
    """Use try which should not have any output"""
    output = tackle('method-except.yaml')
    assert output['compact'] == 'foo'
    assert output['str'] == 'foo'
    assert output['dic']['stuff'] == '{{stuff}}'
    assert output['dict_render_block'] == {'stuff': '{{stuff}}'}
    assert output['stuff'] == 'things'
    assert output['listed']['hook_call'][1]['stuff'] == 'things'


def test_parser_methods_when(fixture_dir):
    """Use try which should not have any output"""
    output = tackle('method-when.yaml')
    assert 'expanded' not in output


def test_parser_methods_else_hooks(fixture_dir):
    """Use try which should not have any output"""
    output = tackle('method-else.yaml')
    assert output['compact'] == 'foo'
    assert output['str'] == 'foo'
    assert output['dict_render']['stuff'] == '{{stuff}}'
    assert output['str_render_block'] == 'things'
    assert output['dict_render_block'] == {'stuff': '{{stuff}}'}
    assert output['stuff'] == 'things'
    assert output['listed']['hook_call'][1]['stuff'] == 'things'


def test_parser_list_comprehension(fixture_dir):
    """Test that we can do list comprehensions."""
    output = tackle('list-comprehension.yaml')
    assert len(output['nodes']) == 1


def test_parser_validation_with_try_except(fixture_dir):
    """Test that we can do list comprehensions."""
    output = tackle('try-validation-except.yaml')
    assert 'p' in output['call']
