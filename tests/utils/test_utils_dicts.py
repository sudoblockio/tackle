"""Tests for tackle.utils.dicts"""
import pytest
from ruamel.yaml import YAML

from tackle.utils.dicts import (
    encode_list_index,
    decode_list_index,
    nested_set,
    nested_get,
    nested_delete,
    # set_key,
    cleanup_unquoted_strings,
)

ZERO_INDEX = encode_list_index(0)


def test_index_encoding():
    """Test encoding function."""
    assert decode_list_index(encode_list_index(1)) == 1


NESTED_SET_FIXTURES = [
    # Indexed as output, key_path, expected_output
    ({}, ['foo'], {'foo': True}),
    ({}, ['one', 'two', 'three'], {'one': {'two': {'three': True}}}),
    ({}, ['this', 'lists', ZERO_INDEX], {'this': {'lists': [True]}}),
    (
        {},
        ['this', 'lists', ZERO_INDEX, 'one', 'two'],
        {'this': {'lists': [{'one': {'two': True}}]}},
    ),
    (
        {},
        ['this', 'lists', ZERO_INDEX, 'one', 'two', ZERO_INDEX],
        {'this': {'lists': [{'one': {'two': [True]}}]}},
    ),
    (
        {},
        ['this', 'lists', ZERO_INDEX, 'one', 'two', ZERO_INDEX, 'one', 'two', 'three'],
        {'this': {'lists': [{'one': {'two': [{'one': {'two': {'three': True}}}]}}]}},
    ),
    ({'bar': 2}, ['foo'], {'bar': 2, 'foo': True}),
    ({'bar': 2}, ['one', 'two', 'three'], {'bar': 2, 'one': {'two': {'three': True}}}),
    ({'bar': 2}, ['this', 'lists', ZERO_INDEX], {'bar': 2, 'this': {'lists': [True]}}),
    (
        {},
        ['this', ZERO_INDEX, 'one', 'two', ZERO_INDEX],
        {'this': [{'one': {'two': [True]}}]},
    ),
    ({}, ['this', ZERO_INDEX, 'one'], {'this': [{'one': True}]}),
    (
        {},
        ['this', 'that', 'foo', ZERO_INDEX, 'one'],
        {'this': {'that': {'foo': [{'one': True}]}}},
    ),
    (
        {'this': {'that': {'foo': [{'one': 1}]}}},
        ['this', 'that', 'foo', encode_list_index(1), 'two'],
        {'this': {'that': {'foo': [{'one': 1}, {'two': True}]}}},
    ),
    (
        {'this': {'lists': [{'one': {'two': 1}}]}},
        ['this', 'lists', ZERO_INDEX, 'one', 'three'],
        {'this': {'lists': [{'one': {'two': 1, 'three': True}}]}},
    ),
    (
        {'this': {'lists': [{'one': {'two': 1}}]}},
        ['this', 'lists', encode_list_index(1), 'one', 'three'],
        {'this': {'lists': [{'one': {'two': 1}}, {'one': {'three': True}}]}},
    ),
    (
        {'foo': ['bar'], 'this': [{'foo': []}]},
        ['this', encode_list_index(0), 'foo', encode_list_index(0), 'one'],
        {'foo': ['bar'], 'this': [{'foo': [{'one': True}]}]},
    ),
    (
        {'this': {'lists': [{'one': {'two': 1}}]}},
        ['this', 'lists', encode_list_index(1), 'one', 'three'],
        {'this': {'lists': [{'one': {'two': 1}}, {'one': {'three': True}}]}},
    ),
    ({}, ['this', ZERO_INDEX, 'one', ZERO_INDEX], {'this': [{'one': [True]}]}),
    (
        {},
        ['this', encode_list_index(0), 'foo', encode_list_index(0), 'one'],
        {'this': [{'foo': [{'one': True}]}]},
    ),
    (
        {},
        ['this', encode_list_index(0), 'foo', 'one'],
        {'this': [{'foo': {'one': True}}]},
    ),
    (
        {},
        ['this', ZERO_INDEX, ZERO_INDEX, 'foo'],
        {'this': [[{'foo': True}]]},
    ),
    (
        {'stuff': ['things']},
        ['stuff', encode_list_index(1), encode_list_index(0)],
        {'stuff': ['things', [True]]},
    ),
    (
        [{'stuff': False}],
        [encode_list_index(1), 'stuff', encode_list_index(0)],
        [{'stuff': False}, {'stuff': [True]}],
    ),
    (
        [],
        [encode_list_index(0), 'stuff', encode_list_index(0)],
        [{'stuff': [True]}],
    ),
    (
        [],
        [encode_list_index(0), 'stuff', encode_list_index(0)],
        [{'stuff': [True]}],
    ),
    # # This test is breaking
    # (
    #     {'stuff': ['things', [{'foo': ['bar', ['baz']]}]]},
    #     ['stuff', encode_list_index(1), encode_list_index(0), 'foo', encode_list_index(1)],
    #     {'stuff': ['things', [{'foo': ['bar', True]}]]},
    # ),
]


@pytest.mark.parametrize("output,key_path,expected_output", NESTED_SET_FIXTURES)
def test_nested_append_bytes(output, key_path, expected_output):
    """Test setting elements in list."""
    nested_set(output, key_path, True)
    assert output == expected_output


NESTED_GET_FIXTURES = [
    ({'foo': 1}, ['foo'], 1),
    (
        {'this': {'that': {'foo': [{'one': 1}, {'one': 'foo'}]}}},
        ['this', 'that', 'foo', encode_list_index(1), 'one'],
        'foo',
    ),
    ({'list': [{'->': 'var this'}]}, ['list', ZERO_INDEX, '->'], 'var this'),
    (
        {'list': [{'->': 'var this'}, {'key->': 'var this'}]},
        ['list', b'\x00\x01', 'key->'],
        'var this',
    ),
    ({'foo': [1]}, ['foo', ZERO_INDEX], 1),
]


@pytest.mark.parametrize("input,key_path,expected_output", NESTED_GET_FIXTURES)
def test_nested_get(input, key_path, expected_output):
    """Test getting based on key path."""
    output = nested_get(input, key_path)

    assert output == expected_output


NESTED_DELETE_FIXTURES = [
    ({'foo': 1}, ['foo'], {}),
    ({'foo': 1, 'bar': 1}, ['foo'], {'bar': 1}),
    ({'foo': 'baz', 'bar': 1}, ['foo', 'baz'], {'foo': None, 'bar': 1}),
    ({'list': [{'->': 'var this'}]}, ['list', ZERO_INDEX, '->'], {'list': []}),
    (
        {'list': [{'->': 'var this'}, 'foo']},
        ['list', ZERO_INDEX, '->'],
        {'list': ['foo']},
    ),
    (
        {'this': {'that': {'foo': [{'one': 1}, {'one': 'foo'}]}}},
        ['this', 'that', 'foo', encode_list_index(1), 'one'],
        {'this': {'that': {'foo': [{'one': 1}]}}},
    ),
    (
        {'this': {'that': {'foo': [{'one': 1}, {'one': 'foo'}]}}},
        ['this', 'that', 'foo', encode_list_index(1)],
        {'this': {'that': {'foo': [{'one': 1}]}}},
    ),
    (
        {'this': {'that': {'foo': [{'one': 1}, {'one': 'foo', 'two': 'boo'}]}}},
        ['this', 'that', 'foo', encode_list_index(1), 'one'],
        {'this': {'that': {'foo': [{'one': 1}, {'two': 'boo'}]}}},
    ),
    ({'foo': {'baz': 1, 'bar': 1}}, ['foo', 'bar'], {'foo': {'baz': 1}}),
    ({'foo': 'bar', 'baz': 1}, ['foo', 'bar'], {'foo': None, 'baz': 1}),
    ({'foo': {'bar': 1, 'baz': 1}}, ['foo', 'bar'], {'foo': {'baz': 1}}),
    ({'foo': {'bar': 1}, 'baz': 1}, ['foo', 'bar'], {'foo': {}, 'baz': 1}),
    ({'foo': 'bar'}, ['foo', 'bar'], {'foo': None}),
    (
        {'list': [{'->': 'var this'}]},
        ['list', ZERO_INDEX, '->', 'var this'],
        {'list': [{'->': None}]},
    ),
    (
        {'list': ['foo', ['a', 'embedded', 'list']]},
        ['list', encode_list_index(1)],
        {'list': ['foo']},
    ),
    (
        {'list': ['foo', ['a', 'embedded', 'list']]},
        ['list', encode_list_index(1), encode_list_index(0)],
        {'list': ['foo', ['embedded', 'list']]},
    ),
]


@pytest.mark.parametrize("input,key_path,expected_output", NESTED_DELETE_FIXTURES)
def test_nested_delete(input, key_path, expected_output):
    """Test deletion based on key path."""
    nested_delete(input, key_path)
    assert input == expected_output


CLEANUP_UNQUOTED_STRINGS_FIXTURES = [
    (
        """
        foo: bar
        """,
        {'foo': 'bar'},
    ),
    (
        """
        foo: {{bar}}
        """,
        {'foo': '{{bar}}'},
    ),
    (
        """
        foo:
          bar: {{baz}}
        """,
        {'foo': {'bar': '{{baz}}'}},
    ),
    (
        """
        foo:
          bar:
            - {{baz}}
        """,
        {'foo': {'bar': ['{{baz}}']}},
    ),
    (
        """
        foo:
          bar:
            - baz: 1
              bing: {{baz}}
        """,
        {'foo': {'bar': [{'baz': 1, 'bing': '{{baz}}'}]}},
    ),
    (
        """
        foo:
          bar:
            - baz: 1
              bing: baz
        """,
        {'foo': {'bar': [{'baz': 1, 'bing': 'baz'}]}},
    ),
]


@pytest.mark.parametrize("input,expected_output", CLEANUP_UNQUOTED_STRINGS_FIXTURES)
def test_utils_dicts_cleanup_unquoted_strings(input, expected_output):
    """Test deletion based on key path."""
    yaml = YAML()
    input_dict = yaml.load(input)

    cleanup_unquoted_strings(input_dict)
    assert input_dict == expected_output
