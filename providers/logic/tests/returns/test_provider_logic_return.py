import pytest

from tackle import tackle


@pytest.mark.parametrize(
    'fixture',
    [
        'basic',
        'render',
        'special-key-bool',
    ],
)
def test_hook_return_basic(fixture):
    output = tackle(f'{fixture}.yaml')

    # Output should always just be a true bool
    assert isinstance(output, bool)
    assert output


def test_hook_return_render():
    """String values are just rendered."""
    output = tackle('special-key-render.yaml')

    assert output == 'hello bar'


# def test_hook_return_hook_call():
#     output = tackle('hook-call.yaml')
#
#     assert output


def test_hook_return_hook_call():
    output = tackle('foo')

    assert output
