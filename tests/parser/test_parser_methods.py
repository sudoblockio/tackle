import yaml
from tackle import tackle


def test_parser_methods_merge(change_curdir_fixtures):
    with open('petstore.yaml') as f:
        expected_output = yaml.safe_load(f)

    output = tackle('merge-petstore-compact.yaml')
    assert output == expected_output


def test_parser_methods_try(change_curdir_fixtures):
    """Use try which should not have any output"""
    output = tackle('try-method.yaml')
    assert output == {}
