import pytest

from tackle import tackle


@pytest.mark.parametrize(
    'fixture',
    [
        'map',
        # 'list',
        # 'str',
    ],
)
def test_hook_while(fixture):
    """"""
    output = tackle(f'{fixture}.yaml')
    # Assertions in fixture
    assert output
