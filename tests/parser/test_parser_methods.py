import yaml
from tackle import tackle


def test_parser_methods_merge(change_curdir_fixtures):
    with open('petstore.yaml') as f:
        expected_output = yaml.safe_load(f)

    output = tackle('merge-petstore-compact.yaml')
    assert output == expected_output


def test_parser_methods_try(change_curdir_fixtures):
    """Use try which should not have any output"""
    output = tackle('method-try.yaml')
    assert output == {}


def test_parser_methods_when(change_curdir_fixtures):
    """Use try which should not have any output"""
    output = tackle('method-when.yaml')
    assert 'expanded' not in output


def test_parser_methods_else_hooks(change_curdir_fixtures):
    """Use try which should not have any output"""
    output = tackle('method-else.yaml')
    assert output['compact'] == 'foo'
    assert output['str'] == 'foo'
    assert output['dict_render']['stuff'] == '{{stuff}}'
    assert output['str_render_block'] == 'things'
    assert output['dict_render_block'] == {'stuff': '{{stuff}}'}
    assert output['stuff'] == 'things'
