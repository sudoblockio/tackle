import os

from tackle import tackle


def test_function_field_default_with_hooks(chdir):
    """Check that when a declarative hook's default is a hook that it is parsed."""
    chdir(os.path.join('fixtures', 'field-hooks'))
    output = tackle('field-hooks.yaml')

    assert output['call']['literal_compact'] == 'foo'
    assert output['call']['literal_expanded'] == 'foo'
    assert output['call']['field_default_compact'] == 'foo'
