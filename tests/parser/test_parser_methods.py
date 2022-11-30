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


def test_parser_methods_merge_list_value(change_curdir_fixtures):
    """Validate that when in a list, running a hook with a merge overwrites the list."""
    # Note: this is kind of strong... But what else is it supposed to mean? Don't use
    # merge for values...
    output = tackle('merge-list-value.yaml')
    assert output['resources'] == 'foo'


def test_parser_methods_merge_list_loop(change_curdir_fixtures):
    """
    Validate that when in a list, running a hook in a for loop with a merge appends to
     the list.
    """
    output = tackle('merge-list-loop.yaml')
    assert len(output['resources']) == 5


def test_parser_methods_merge_dict_loop_dict(change_curdir_fixtures):
    """
    Validate that when in a dict, running a hook in a for loop with a merge adds new
     keys to the output.
    """
    # TODO: Associated with https://github.com/robcxyz/tackle/issues/107
    output = tackle('merge-dict-loop-dict.yaml')
    assert output['resources']['foo-2']


def test_parser_methods_merge_dict_loop_exception(change_curdir_fixtures):
    """
    Validate exception that when in a dict, running a hook in a for loop with a merge
     with the hook output being a value.
    """
    with pytest.raises(exceptions.AppendMergeException):
        tackle('merge-dict-loop-exception.yaml')


def test_parser_methods_try(chdir):
    """Use try which should not have any output"""
    chdir("method-fixtures")
    output = tackle('method-try.yaml')
    assert output == {}


def test_parser_methods_except(chdir):
    """Use try which should not have any output"""
    chdir("method-fixtures")
    output = tackle('method-except.yaml')
    assert output['compact'] == 'foo'
    assert output['str'] == 'foo'
    assert output['dic']['stuff'] == '{{stuff}}'
    assert output['dict_render_block'] == {'stuff': '{{stuff}}'}
    assert output['stuff'] == 'things'
    assert output['listed']['hook_call'][1]['stuff'] == 'things'


def test_parser_methods_when(chdir):
    """Use try which should not have any output"""
    chdir("method-fixtures")
    output = tackle('method-when.yaml')
    assert 'expanded' not in output


def test_parser_methods_else_hooks(chdir):
    """Use try which should not have any output"""
    chdir("method-fixtures")
    output = tackle('method-else.yaml')
    assert output['compact'] == 'foo'
    assert output['str'] == 'foo'
    assert output['dict_render']['stuff'] == '{{stuff}}'
    assert output['str_render_block'] == 'things'
    assert output['dict_render_block'] == {'stuff': '{{stuff}}'}
    assert output['stuff'] == 'things'
    assert output['listed']['hook_call'][1]['stuff'] == 'things'


def test_parser_list_comprehension(chdir):
    """Test that we can do list comprehensions."""
    chdir("method-fixtures")
    output = tackle('list-comprehension.yaml')
    assert len(output['nodes']) == 1


def test_parser_validation_with_try_except(chdir):
    """Test that we can do list comprehensions."""
    chdir("method-fixtures")
    output = tackle('try-validation-except.yaml')
    assert 'p' in output['call']
