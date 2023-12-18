import pytest

from tackle import tackle


@pytest.mark.parametrize(
    'fixture',
    [
        'basic',
        'render',
        'special-key',
    ],
)
def test_hook_return_basic(fixture):
    output = tackle(f'{fixture}.yaml')

    # Output should always just be a true bool
    assert isinstance(output, bool)


def test_hook_return_hook_call():
    output = tackle('hook-call.yaml')

    assert output
