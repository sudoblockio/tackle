from ipaddress import IPv4Address
from typing import Any, Dict, List, Union

import pytest
from pydantic import BaseModel

from tackle import BaseHook, tackle
from tackle.hooks import create_dcl_hook
from tackle.utils.type_strings import field_to_string, type_to_string

TYPE_FIXTURES = [
    (dict, "dict"),
    (Dict, "Dict"),
    (list, "list"),
    (List, "List"),
    (Any, "Any"),
    (IPv4Address, "IPv4Address"),
    (Union[dict, list], "Union[dict, list]"),
    (str | int, "str | int"),
]


@pytest.mark.parametrize("type_,expected_output", TYPE_FIXTURES)
def test_hook_type_to_string(type_, expected_output):
    """Check we can convert a type object to string properly."""
    output = type_to_string(type_)
    assert output == expected_output


def test_hook_type_to_string_python_types():
    class Foo(BaseModel):
        foo: str

    class MyHook(BaseHook):
        a_str: str
        a_union: Union[str, int]
        a_new_union: str | int
        embedded: Foo
        embedded_list: list[Foo]

    my_hook_fields = MyHook.model_fields

    assert field_to_string(my_hook_fields['a_str']) == 'str'
    assert field_to_string(my_hook_fields['a_new_union']) == 'str | int'
    assert field_to_string(my_hook_fields['a_union']) == 'Union[str, int]'
    assert field_to_string(my_hook_fields['embedded']) == 'Foo'
    # TODO: Broken - goes to list
    # assert field_to_string(my_hook_fields['embedded_list']) == 'list[Foo]'


def test_hook_type_to_string_dcl_types(cd_fixtures):
    context = tackle('field-to-string-types.yaml', return_context=True)

    Hook = context.hooks.public['MyHook']
    Hook = create_dcl_hook(
        context=context,
        hook_name="MyHook",
        hook_input_raw=Hook.input_raw,
    )
    my_hook_fields = Hook.model_fields

    assert field_to_string(my_hook_fields['a_str']) == 'str'
    assert field_to_string(my_hook_fields['a_new_union']) == 'str | int'
    assert field_to_string(my_hook_fields['a_union']) == 'Union[str, int]'
    assert field_to_string(my_hook_fields['embedded']) == 'Foo'
