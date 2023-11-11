import pytest

from tackle import tackle


def test_hooks_method():
    """Check that methods work"""
    output = tackle('method-hook.yaml')

    assert output['method_kwarg'] == {'bar': 'baz', 'foo': 'bang'}
    assert output['base_kwarg'] == {'bar': 'bang', 'foo': 'bing'}
    assert output['jinja_method'] == {'bar': 'baz', 'foo': 'bang'}
    assert output['jinja_base'] == {'bar': 'bang'}


def test_hooks_method_simple():
    """Check that we can create a method."""
    output = tackle('method-single.yaml')
    assert output['do'] == {"v": ["Hello", "world!"]}


def test_hooks_method_embed():
    """Check that we can create a method."""
    output = tackle('method-embed.yaml')
    assert output['do']['v'] == ['Hello', 'world!']


def test_hooks_method_inherit():
    """Check that we can create a method."""
    output = tackle('method-inherit.yaml')
    assert output == {"t": "fooo"}


def test_hooks_method_args():
    """Check that we can create a method that takes args."""
    output = tackle('method-args.yaml')
    assert output == {'foo': {'in': 'bar'}}


def test_hooks_method_call_from_default():
    """
    Check that we can create a method that takes args.
    See https://github.com/robcxyz/tackle/issues/99
    """
    output = tackle('method-call-from-default.yaml', target='foo')
    assert output['hi'] == 'Hello foo'


def test_hooks_method_maintain_context():
    """Check a method that carries a context with it from the parent object."""
    output = tackle('method-maintain-context.yaml')
    assert output['do_greeter']['v'] == ['Hello', 'world!']
    assert output['jinja_call']['v'] == ['Hello', 'world!']


def test_hooks_method_nested():
    """Check that we can create a method."""
    output = tackle('method-nested-hook.yaml')
    assert output['jinja_method_home']['destination'] == "earth"
    assert output['jinja_method_home'] == output['t_home']


def test_hooks_method_override():
    """
    Check that when we call methods that attributes are properly overridden if they
     exist in the base.
    """
    output = tackle('method-nested-override.yaml')
    assert output['method_overlap_jinja']['home'] == 'earth'
    assert output['method_overlap_compact']['home'] == 'foo'
    assert output['attribute_override_jinja']['home'] == 'bing'
    assert output['attribute_override_compact']['home'] == 'bing'
    assert output['nested_jinja']['home'] == 'baz'
    assert output['nexted_compact']['home'] == 'baz'


def test_hooks_method_field_loop_dict():
    """
    Check for a bug as described in https://github.com/sudoblockio/tackle/issues/168
     where loops of dicts parsed correctly.
    """
    output = tackle('method-nested-override.yaml')
