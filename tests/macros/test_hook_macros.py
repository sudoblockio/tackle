import pytest

from tackle.macros.hook_macros import hook_macros

HOOK_INPUT_FIXTURES = [
    # hook_input,expected_output
    ({'stuff': 'things'}, {'stuff': {'default': 'things', 'type': 'str'}}),
    (
        {'stuff': 'str'},
        {'stuff': {'type': 'str'}},
    ),
    (
        {'stuff': 'list'},
        {'stuff': {'type': 'list'}},
    ),
    (
        {'stuff': {'type': 'list'}},
        {'stuff': {'type': 'list'}},
    ),
    (
        {'stuff': {'default': 'foo'}},
        {
            'stuff': {
                'type': 'str',
                'default': 'foo',
            }
        },
    ),
    (
        {
            'stuff': {
                'things': 'foo',
            }
        },
        {
            'stuff': {
                'type': 'Any',
                'default_factory': {'things': 'foo'},
            }
        },
    ),
    (
        {
            'stuff': [
                {
                    'things': 'foo',
                }
            ]
        },
        {
            'stuff': {
                'type': 'list',
                'default_factory': [{'things': 'foo'}],
            }
        },
    ),
    (
        {'stuff': {'->': 'foo', 'bar': 'bar'}},
        {
            'stuff': {
                'type': 'Any',
                'default_factory': {
                    'stuff': {'->': 'foo', 'bar': 'bar'},
                    'return->': 'stuff',
                },
            }
        },
    ),
    (
        {
            'stuff<-': {
                'things': 'foo',
            }
        },
        {
            'stuff': {
                '<-': {'things': 'foo'},
            }
        },
    ),
    (
        {'stuff': {'->': 'foo', 'type': 'bar'}},
        {
            'stuff': {
                'type': 'Any',
                'default_factory': {
                    'stuff': {'->': 'foo', 'type': 'bar'},
                    'return->': 'stuff',
                },
            }
        },
    ),
    (
        {'stuff': {'default_factory->': 'foo', 'bar': 'bar', 'type': 'str'}},
        {
            'stuff': {
                'type': 'str',
                'bar': 'bar',
                'default_factory': {'stuff': {'->': 'foo'}, 'return->': 'stuff'},
            }
        },
    ),
    (
        {'stuff': {'default_factory': {'->': 'foo', 'bar': 'bar'}, 'type': 'str'}},
        {
            'stuff': {
                'type': 'str',
                'default_factory': {
                    'stuff': {'->': 'foo', 'bar': 'bar'},
                    'return->': 'stuff',
                },
            }
        },
    ),
]


@pytest.mark.parametrize("hook_input,expected_output", HOOK_INPUT_FIXTURES)
def test_macros_hook_macros(context, hook_input, expected_output):
    """Check every case for how we could get inputs."""
    output = hook_macros(context=context, hook_input_raw=hook_input, hook_name="")

    assert output == expected_output


FIELD_HOOK_INPUT_FIXTURES: list[dict] = [
    {"field": {"default_factory": {"tmp->": "literal foo", "return->": "{{tmp}}"}}},
    {"field->": "literal foo"},
    {"field": {"->": "literal foo"}},
    {"field": {"default->": "literal foo"}},
    {"field": {"default_factory->": "literal foo"}},
    {"field": {"default_factory": {"->": "literal foo"}}},
    # # TODO: Support moving default arrow to default_factory
    # {"field": {"default": {"->": "literal foo"}}},
]


@pytest.mark.parametrize("hook_input_raw", FIELD_HOOK_INPUT_FIXTURES)
def test_macros_hook_macros_field_hooks(context, hook_input_raw):
    output = hook_macros(context=context, hook_input_raw=hook_input_raw, hook_name="")

    assert 'default_factory' in output['field']
