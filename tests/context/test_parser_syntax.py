from collections import OrderedDict
import yaml
import pytest

from tackle.models import Context
from tackle.parser import walk_context, nested_set, nested_get

FIXTURES = [
    'simple_map.yaml',
    'long_list.yaml',
    'dict_list_dict.yaml',
    'complex_list.yaml',
    'single_level_list.yaml',
    'merge-key-simple.yaml',
    'k8s-deployment.yaml',
    'docker-compose.yml',
    'petstore.yaml',
]


@pytest.mark.parametrize("fixture", FIXTURES)
def test_parser_fixture_equals_input(change_curdir_fixtures, fixture):
    with open(fixture) as f:
        input_dict = yaml.safe_load(f)

    context = Context(input_dict=input_dict)
    walk_context(context)
    assert dict(context.output_dict) == context.input_dict


# Rules
# Lists that start with a string are a key
# Lists that start with a int are an index to a list

# Issues
# When keys are numbers
#   - Solution -> indexer not int but bytes (obscure key making collisions harder)

KEY_PATHS = [
    ({}, ['foo'], {'foo': True}),
    ({}, ['one', 'two', 'three'], {'one': {'two': {'three': True}}}),
    ({}, ['this', 'lists', [0]], {'this': {'lists': [True]}}),
    (
        {},
        ['this', 'lists', [0], 'one', 'two'],
        {'this': {'lists': [{'one': {'two': True}}]}},
    ),
    (
        {},
        ['this', 'lists', [0], 'one', 'two', [0]],
        {'this': {'lists': [{'one': {'two': [True]}}]}},
    ),
    (
        {},
        ['this', 'lists', [0], 'one', 'two', [0], 'one', 'two', 'three'],
        {'this': {'lists': [{'one': {'two': [{'one': {'two': {'three': True}}}]}}]}},
    ),
    ({'bar': 2}, ['foo'], {'bar': 2, 'foo': True}),
    ({'bar': 2}, ['one', 'two', 'three'], {'bar': 2, 'one': {'two': {'three': True}}}),
    ({'bar': 2}, ['this', 'lists', [0]], {'bar': 2, 'this': {'lists': [True]}}),
    (
        {'this': {'lists': [{'one': {'two': 1}}]}},
        ['this', 'lists', [0], 'one', 'three'],
        {'this': {'lists': [{'one': {'two': 1, 'three': True}}]}},
    ),
    (
        {'this': {'lists': [{'one': {'two': 1}}]}},
        ['this', 'lists', [1], 'one', 'three'],
        {'this': {'lists': [{'one': {'two': 1}}, {'one': {'three': True}}]}},
    ),
    (
        {'this': {'lists': [{'one': {'two': 1}}]}},
        ['this', 'lists', [1], 'one', 'three'],
        {'this': {'lists': [{'one': {'two': 1}}, {'one': {'three': True}}]}},
    ),
    ({}, ['this', [0], 'one', 'two', [0]], {'this': [{'one': {'two': [True]}}]}),
    ({}, ['this', [0], 'one', [0]], {'this': [{'one': [True]}]}),
    ({}, ['this', [0], 'one'], {'this': [{'one': True}]}),
    (
        {},
        ['this', 'that', 'foo', [0], 'one'],
        {'this': {'that': {'foo': [{'one': True}]}}},
    ),
    (
        {'this': {'that': {'foo': [{'one': 1}]}}},
        ['this', 'that', 'foo', [1], 'one'],
        {'this': {'that': {'foo': [{'one': 1}, {'one': True}]}}},
    ),
]


@pytest.mark.parametrize("output,key_path,expected_output", KEY_PATHS)
def test_nested_append(output, key_path, expected_output):
    nested_set(output, key_path, True)
    assert output == expected_output


KEY_GET_PATHS = [
    ({'this': {'that': {'foo': [{'one': 1}]}}}, ['this', 'that', 'foo', [0], 'one'], 1),
]


@pytest.mark.parametrize("output,key_path,expected_output", KEY_GET_PATHS)
def test_nested_get(output, key_path, expected_output):
    output = nested_get(output, key_path)
    assert output == expected_output


def test_tackle_call_types(change_curdir_fixtures):
    with open('tackle_map.yaml') as f:
        input_dict = yaml.safe_load(f)

    context = Context(input_dict=input_dict)
    walk_context(context)

    assert context.output_dict
