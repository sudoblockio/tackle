import pytest

from tackle import tackle
from tackle import exceptions
from tackle.parser import parse_function_type
from tackle.models import Context


@pytest.fixture()
def context_fixture(change_dir):
    return Context(
        hook_dirs=['.hooks'],
        calling_file='',
        private_hooks={},
    )


BASE_ID = "pydantic.main.Base"
TYPE_FIXTURES = [
    ('Base', f"<class '{BASE_ID}'>"),
    ('list[str]', 'list[str]'),
    ('list[str, int]', 'list[str, int]'),
    ('list[Base]', f'list[{BASE_ID}]'),
    ('List[Base]', f'typing.List[{BASE_ID}]'),
    ('dict[str,Base]', f'dict[str, {BASE_ID}]'),
    ('Dict[str, Base]', f'typing.Dict[str, {BASE_ID}]'),
    ('optional[Base]', f'typing.Optional[{BASE_ID}]'),
    ('Optional[Base]', f'typing.Optional[{BASE_ID}]'),
    ('union[Base, str]', f'typing.Union[{BASE_ID}, str]'),
    ('Union[Base, str]', f'typing.Union[{BASE_ID}, str]'),
    ('Optional[Union[Base, str]]', f'typing.Union[{BASE_ID}, str, NoneType]'),
    ('list[Base, dict[str, list]]', f'list[{BASE_ID}, dict[str, list]]'),
    ('list[dict[str, Base], Base]', f'list[dict[str, {BASE_ID}], {BASE_ID}]'),
    ('list[Base, dict[str, Base]]', f'list[{BASE_ID}, dict[str, {BASE_ID}]]'),
]


@pytest.mark.parametrize("type_str,expected_repr", TYPE_FIXTURES)
def test_functions_types_parse_function_type(type_str, expected_repr, context_fixture):
    """
    Check complex type parsing where a `Base` hook is imported from the current
     directory's '.hooks' dir with various typing around it.
    """
    output = parse_function_type(
        context=context_fixture,
        type_str=type_str,
        func_name="foo",
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
def test_functions_types_malformed_field_exceptions(type_str, context_fixture):
    """Check that an error is thrown for bad types."""
    with pytest.raises(exceptions.MalformedFunctionFieldException):
        parse_function_type(
            context=context_fixture,
            type_str=type_str,
            func_name="foo",
        )


@pytest.fixture()
def types_fixtures(chdir):
    chdir('types-fixtures')


def test_functions_types_base(types_fixtures):
    """Check that we can compose a single hook type."""
    output = tackle('base.yaml')
    assert output['check_ok']['bar']['foo'] == 'baz'
    assert output['check_false'] == 1


def test_functions_types_base_embed(types_fixtures):
    """Check that we can compose embedded hook types."""
    output = tackle('base-embed.yaml')
    assert output['check_ok']['bar']['foo2']['foo1'] == 'baz'
    assert output['check_false'] == 1


def test_functions_types_list_base(types_fixtures):
    """Validate a list with hooks."""
    output = tackle('list-base.yaml')
    assert output['check_ok']['bar'][0]['foo'] == 'baz'
    assert output['check_ok']['bar'][1]['foo'] == 'baz2'
    assert output['check_false'] == 1


def test_functions_types_dict_base(types_fixtures):
    """Validate a dict with hooks."""
    output = tackle('dict-base.yaml')
    assert output['check_ok']['bar']['bar']['foo'] == 'baz'
    assert output['check_false'] == 1


def test_functions_composition_enum_basic(types_fixtures):
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
