from ruamel.yaml import YAML
from tackle import tackle


def test_parser_methods_merge(change_curdir_fixtures):
    yaml = YAML()
    with open('petstore.yaml') as f:
        expected_output = yaml.load(f)

    output = tackle('merge-petstore-compact.yaml')
    assert output == expected_output


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
