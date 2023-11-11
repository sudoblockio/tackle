import pytest

from tackle import tackle
from tackle import exceptions
from tackle.cli import main
from tackle.hooks import parse_hook_type
from tackle.factory import new_context


BASE_ID = "tackle.pydantic.create_model.Base"
TYPE_FIXTURES = [
    ('Base', f"<class '{BASE_ID}'>"),
    ('list[str]', 'list[str]'),
    ('list[str, int]', 'list[str, int]'),
    ('list[Base]', f'list[{BASE_ID}]'),
    ('List[Base]', f'typing.List[{BASE_ID}]'),
    ('dict[str,Base]', f'dict[str, {BASE_ID}]'),
    ('Dict[str, Base]', f'typing.Dict[str, {BASE_ID}]'),
    # TODO: Support lower case `optional`? Would require special logic...
    # ('optional[Base]', f'typing.Optional[{BASE_ID}]'),
    # ('union[Base, str]', f'typing.Union[{BASE_ID}, str]'),
    ('Optional[Base]', f'typing.Optional[{BASE_ID}]'),
    ('Union[Base, str]', f'typing.Union[{BASE_ID}, str]'),
    ('Optional[Union[Base, str]]', f'typing.Union[{BASE_ID}, str, NoneType]'),
    ('list[Base, dict[str, list]]', f'list[{BASE_ID}, dict[str, list]]'),
    ('list[dict[str, Base], Base]', f'list[dict[str, {BASE_ID}], {BASE_ID}]'),
    ('list[Base, dict[str, Base]]', f'list[{BASE_ID}, dict[str, {BASE_ID}]]'),
]


@pytest.mark.parametrize("type_str,expected_repr", TYPE_FIXTURES)
def test_hooks_types_parse_function_type(type_str, expected_repr):
    """
    Check complex type parsing where a `Base` hook is imported from the current
     directory's '.hooks' dir with various typing around it.
    """
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
    assert output['check_ok']['bar']['foo2']['foo1'] == 'baz'
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


# def test_hooks_types_enum_types():
#     """Check enums with types."""
#     output = tackle('enum-render.yaml')
#
#     assert output['failure']
#     assert output['failure_default']
#
#     assert output['success']['color'] == 'blue'
#     assert output['success']['color_default'] == 'red'
#     assert output['success_default']['color'] == 'blue'
#     assert output['success_default']['color_default'] == 'green'

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


def test_hooks_types_help_basic():
    """Check that special field types are rendered properly in the help screen."""
    output = main(['help-basic.yaml', 'help'])

    assert output


@pytest.mark.parametrize("file", [
    'types-pydantic.yaml',
    'types-pydantic-network.yaml',
    'types-network.yaml',
    'types-datetime.yaml',
])
def test_hooks_types_pydantic_types(file):
    """Check that we can use pydantic types in a hook field."""
    output = tackle(file)

    assert output['call']['a_field']
    assert output['error'] == 1
