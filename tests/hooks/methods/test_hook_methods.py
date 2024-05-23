from tackle import tackle


def test_hooks_method():
    """Check that methods work"""
    output = tackle('hook.yaml')

    assert output['method_kwarg'] == {'bar': 'baz', 'foo': 'bang'}
    assert output['base_kwarg'] == {'bar': 'bang', 'foo': 'bing'}
    assert output['jinja_method'] == {'bar': 'baz', 'foo': 'bang'}
    assert output['jinja_base'] == {'bar': 'bang'}


def test_hooks_method_simple():
    """Check that we can create a method."""
    output = tackle('single.yaml')
    assert output['do'] == {"v": ["Hello", "world!"]}


def test_hooks_method_embed():
    """Check that we can create a method."""
    output = tackle('embed.yaml')
    assert output['do']['v'] == ['Hello', 'world!']


def test_hooks_method_inherit():
    """Check that we can call an inherited method."""
    output = tackle('inherit.yaml')

    assert output['call']['foo'] == 'bar'


def test_hooks_method_args():
    """Check that we can create a method that takes args."""
    output = tackle('args.yaml')
    assert output == {'foo': {'my_var': 'bar'}}


def test_hooks_method_call_from_default():
    """
    Check that we can create a method that takes args.
    See https://github.com/robcxyz/tackle/issues/99
    """
    output = tackle('call-from-default.yaml', target='foo')
    assert output['hi'] == 'Hello foo'


def test_hooks_method_maintain_context():
    """Check a method that carries a context with it from the parent object."""
    output = tackle('maintain-context.yaml')
    assert output['do_greeter']['v'] == ['Hello', 'world!']
    assert output['jinja_call']['v'] == ['Hello', 'world!']


def test_hooks_method_nested():
    """Check that we can create a method."""
    output = tackle('nested-hook.yaml')
    assert output['jinja_method_home']['destination'] == "earth"
    assert output['jinja_method_home'] == output['t_home']


def test_hooks_method_override():
    """
    Check that when we call methods that attributes are properly overridden if they
     exist in the base.
    """
    output = tackle('nested-override.yaml')
    assert output['method_overlap_jinja']['home'] == 'earth'
    assert output['method_overlap_compact']['home'] == 'foo'
    assert output['attribute_override_jinja']['home'] == 'bing'
    assert output['attribute_override_compact']['home'] == 'bing'
    assert output['nested_jinja']['home'] == 'baz'
    assert output['nexted_compact']['home'] == 'baz'


def test_hooks_method_no_default():
    """Assert that method calls with base fields with no default can be run."""
    o = tackle('call-no-default.yaml')
    assert o['compact']['v'] == 'foo'
    assert o['compact'] == o['expanded']
    assert o['jinja_base']['word'] == 'foo'
    assert o['jinja_method']['v'] == 'foo'


def test_hooks_method_external_call_required():
    """Make sure required variables are assessed properly."""
    output = tackle('external-call-required.yaml', 'MyHook', 'MyMethod', a_var=1)

    assert output == 1


def test_hooks_method_call_hook_from_method():
    output = tackle('call-hook-from-method.yaml', 'MyMethod', 'Method1')

    assert output


def test_hooks_method_call_hook_from_import():
    output = tackle('call-hook-from-import.yaml')

    assert output
