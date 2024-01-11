import pytest

from tackle import exceptions, tackle
from tackle.factory import new_context
from tackle.hooks import parse_hook_type

BASE_ID = "tackle.pydantic.create_model.Base"


@pytest.mark.parametrize(
    "type_str,expected_repr",
    [
        ('Base', f"<class '{BASE_ID}'>"),
        ('list[str]', 'list[str]'),
        ('list[str, int]', 'list[str, int]'),
        ('list[Base]', f'list[{BASE_ID}]'),
        ('List[Base]', f'typing.List[{BASE_ID}]'),
        ('dict[str,Base]', f'dict[str, {BASE_ID}]'),
        ('Dict[str, Base]', f'typing.Dict[str, {BASE_ID}]'),
        ('optional[Base]', f'typing.Optional[{BASE_ID}]'),
        ('union[Base, str]', f'typing.Union[{BASE_ID}, str]'),
        ('Optional[Base]', f'typing.Optional[{BASE_ID}]'),
        ('Union[Base, str]', f'typing.Union[{BASE_ID}, str]'),
        ('Optional[Union[Base, str]]', f'typing.Union[{BASE_ID}, str, NoneType]'),
        ('list[Base, dict[str, list]]', f'list[{BASE_ID}, dict[str, list]]'),
        ('list[dict[str, Base], Base]', f'list[dict[str, {BASE_ID}], {BASE_ID}]'),
        ('list[Base, dict[str, Base]]', f'list[{BASE_ID}, dict[str, {BASE_ID}]]'),
        ('str | int', 'typing.Union[str, int]'),
        ('str|int', 'typing.Union[str, int]'),
        ('dict[str | int, str]', 'dict[typing.Union[str, int], str]'),
    ],
)
def test_hooks_types_parse_function_type(type_str, expected_repr):
    """
    Check complex type parsing where a `Base` hook is imported from the current
     directory's '.hooks' dir with various typing around it.
    """
    # Look in the `.hooks` dir for a hook
    context = new_context()
    output = parse_hook_type(
        context=context,
        type_str=type_str,
        hook_name="foo",
    )
    assert repr(output) == expected_repr


BAD_TYPE_FIXTURES = [
    'NotBase',
    'Str',
    'list[Str]',
    'list[NotBase]',
    'Optional[Base, str]',
]


@pytest.mark.parametrize("type_str", BAD_TYPE_FIXTURES)
def test_hooks_types_malformed_field_exceptions(type_str):
    """Check that an error is thrown for bad types."""
    with pytest.raises(exceptions.MalformedHookFieldException):
        parse_hook_type(
            context=new_context(),
            type_str=type_str,
            hook_name="foo",
        )


def test_hooks_types_base():
    """Check that we can compose a single hook type."""
    output = tackle('base.yaml')
    assert output['check_ok']['bar']['foo'] == 'baz'
    assert output['check_false'] == 1


def test_hooks_types_base_embed():
    """Check that we can compose embedded hook types."""
    output = tackle('base-embed.yaml')
    assert output['check_ok']['bar']['foo2'] == {'foo1': 'baz'}
    assert output['check_ok_render']['bar']['foo2'] == {'foo1': 'baz'}
    assert output['check_false'] == 1


def test_hooks_types_base_default():
    """Check that we can compose hooks with composed defaults."""
    output = tackle('base-default.yaml', 'call_ok_static')
    assert output['bar']['foo'] == 'baz'

    # output = tackle('base-default.yaml', 'call_ok_hook')
    # assert output['bar']['foo'] == 'baz'

    # with pytest.raises(exceptions.MalformedHookFieldException):
    #     output = tackle('base-default.yaml', 'call_false')
    # assert output


def test_hooks_types_list_base():
    """Validate a list with hooks."""
    output = tackle('list-base.yaml')

    assert output['check_ok']['bar'][0]['foo'] == 'baz'
    assert output['check_ok']['bar'][1]['foo'] == 'baz2'
    assert output['check_false'] == 1


def test_hooks_types_dict_base():
    """Validate a dict with hooks."""
    output = tackle('dict-base.yaml')

    assert output['check_ok']['bar']['bar']['foo'] == 'baz'
    assert output['check_false'] == 1


def test_hooks_types_enum_basic():
    """
    Show that we can create enum types, that they fail when we give them some value
     out of its members, and that it is properly deserialized.
    """
    output = tackle('enum-basic.yaml')

    assert output['failure']
    assert output['failure_default']

    assert output['success']['color'] == 'blue'
    assert output['success']['color_default'] == 'red'
    assert output['success_default']['color'] == 'blue'
    assert output['success_default']['color_default'] == 'green'


def test_hooks_types_enum_types():
    """Check enums with types."""
    output = tackle('enum-render.yaml')

    assert output['failure']
    assert output['failure_default']

    assert output['success']['color'] == 'blue'
    assert output['success']['color_default'] == 'red'
    assert output['success_default']['color'] == 'blue'
    assert output['success_default']['color_default'] == 'green'


def test_hooks_types_enum_render():
    """Check that in a dcl hook we can render an enum type from a previous field."""
    # TODO: May not be possible based on new design but achievable with the pre-hook
    #  parsing vs post-hook parsing.
    output = tackle('enum-render.yaml')

    assert output['failure']
    assert output['failure_default']

    assert output['success']['color'] == 'blue'
    assert output['success']['color_default'] == 'red'
    assert output['success_default']['color'] == 'blue'
    assert output['success_default']['color_default'] == 'green'


def test_hooks_types_bool_defaults():
    """Check that when a bool field is default to true that raising flag inverts it."""
    output = tackle('hook-bool-default.yaml')

    assert output['call']['is_true']
    assert not output['call']['is_false']
    assert not output['call_true']['is_true']
    assert output['call_true']['is_false']


@pytest.mark.parametrize(
    "file,expected_value",
    [
        ('types-pydantic.yaml', 1),
        ('types-pydantic-network.yaml', '1.2.3.4'),
        ('types-network.yaml', '1.2.3.4'),
        ('types-lookup.yaml', None),
        ('types-datetime.yaml', "12:30:15"),
        ('types-datetime-timestamp.yaml', '1970-01-01 00:00:00+00:00'),
        ('types-python-pipe.yaml', 'foo'),
        ('types-python-union.yaml', 'foo'),
    ],
)
def test_hooks_types_list(file, expected_value):
    """Check that we can use pydantic types in a hook field."""
    output = tackle(file)

    assert output['call']['a_field'] == expected_value
    assert output['error'] == 1


@pytest.mark.parametrize(
    "input_file,expected_output",
    [
        ('default-dict.yaml', {'a_field': {'bar->': 'literal baz'}}),
        ('default-list.yaml', {'a_field': [{'bar->': 'literal baz'}]}),
        ('default-factory-dict.yaml', {'a_field': {'bar': 'baz'}}),
        ('default-factory-list.yaml', {'a_field': [{'bar': 'baz'}]}),
        ('value-dict.yaml', {'a_field': {'bar': 'baz'}}),
        ('value-list.yaml', {'a_field': ['bar']}),
    ],
)
def test_hooks_types_default_dict(input_file, expected_output):
    """Check that a default dict value works properly."""
    output = tackle(input_file, 'MyHook')

    assert output == expected_output


def test_hooks_default_hook_types():
    output = tackle('default-hook-types.yaml', a_pipe='bar')

    assert output


def test_hooks_python_hook():
    """We can validate data with a python hook."""
    output = tackle('python-hook.yaml')

    assert output['call_py_hook']['foo'] == 'bar'
    assert output['call_a_func'] == 'bar'
    assert output['error_missing'] == 1
    assert output['error_a_func'] == 1
