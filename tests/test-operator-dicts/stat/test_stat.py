# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
from cookiecutter.operators.stat import StatOperator

FIXTURES = ['checkbox_bad.yaml']

context = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'stuff': ['things', 'bears'],
        'foo': {'type': 'stat', 'input': {'bar': 'baz', 'grrr': 'wowzaz'}},
    }
}


def test_stat():
    """Verify simplest functionality."""
    c = StatOperator(context['cookiecutter']['foo'], context)
    d = c.execute()
    assert d == {'bar': 'baz', 'grrr': 'wowzaz'}
