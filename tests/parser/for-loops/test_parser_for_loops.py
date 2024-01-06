import pytest

from tackle import HookCallInput, new_context, tackle
from tackle.parser import get_for_loop_variable_names


@pytest.mark.parametrize(
    "input_string,public_data,index_name,value_name,key_name",
    [
        ("foo", {'foo': []}, 'index', 'item', None),
        ("i, v in foo", {'foo': []}, 'i', 'v', None),
        ("i in foo", {'foo': []}, 'index', 'i', None),
        ("foo", {'foo': {}}, 'index', 'value', "key"),
        ("k in foo", {'foo': {}}, 'index', 'value', "k"),
        ("k, v in foo", {'foo': {}}, 'index', 'v', "k"),
        ("k, v, i in foo", {'foo': {}}, 'i', 'v', "k"),
        ("v in range(1, 10)", {'foo': {}}, 'index', 'v', None),
        ("v in range(1, foo)", {'foo': 3}, 'index', 'v', None),
        ("i in ['foo', 'bar']", {}, 'index', 'i', None),
        ("i in [foo]", {'foo': 'bar'}, 'index', 'i', None),
    ],
)
def test_parser_get_for_loop_variable_names(
    input_string,
    public_data,
    index_name,
    value_name,
    key_name,
):
    """Check we can parse the for loop string properly."""
    context = new_context()
    context.data.public = public_data
    hook_call = HookCallInput(for_=input_string)
    output = get_for_loop_variable_names(context, hook_call)

    assert output.index_name == index_name
    assert output.value_name == value_name
    assert output.key_name == key_name


@pytest.mark.parametrize(
    "fixture",
    [
        'for-list-variable.yaml',
        'for-list-in-variable.yaml',
        'for-list-literal.yaml',
    ],
)
def test_parser_for_loop_list_parameterized(fixture):
    """Check for key with list variable."""
    o = tackle(fixture)
    assert o['expanded_value'] == ['bar', 'baz']
    assert o['expanded_index'] == [0, 1]
    assert o['compact'] == ['bar', 'baz']


@pytest.mark.parametrize(
    "fixture",
    [
        'for-dict-variable.yaml',
        'for-dict-in-variable.yaml',
        'for-dict-literal.yaml',
    ],
)
def test_parser_for_loop_dict_parameterized(fixture):
    """Check for key with dict variable."""
    o = tackle(fixture)
    assert o['expanded_key'] == ['foo', 'baz']
    assert o['expanded_value'] == ['bar', 'bing']
    assert o['expanded_index'] == [0, 1]
    assert o['compact_key'] == ['foo', 'baz']
    assert o['compact_value'] == ['bar', 'bing']
    assert o['compact_index'] == [0, 1]


def test_parser_for_loop_embedded_block():
    output = tackle('embedded-block.yaml')

    assert output['foo'][0]['bar'][1]['j_is'] == 4
    assert output['foo'][1]['bar'][1]['j_is'] == 4
