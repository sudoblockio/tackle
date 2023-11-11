import pytest

from tackle.factory import new_context

# from tackle.hooks import create_default_factory_walker


def test_create_default_factory_walker():
    value = {
        'in': {
            '->': 'literal bar'
        },
        'out': {
            '->': 'return {{in}}'
        },
    }
    factory = create_default_factory_walker(context=new_context(), value=value)
    output = factory()

    assert output == 'bar'


def test_create_default_factory_walker2():
    value = {
        'default': {
            'in': {
                '->': 'literal bar'
            },
            'out': {
                '->': 'return {{in}}'
            },
        },
        'exclude': False,
        'type': 'Any',
        'parse_keys': ['default']
    }

    tmp_context = new_context()
    factory = create_default_factory_walker(context=tmp_context, value=value['default'])
    output = factory()

    assert output == 'bar'
