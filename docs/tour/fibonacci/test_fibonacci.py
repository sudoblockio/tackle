import pytest

from tackle import tackle


@pytest.mark.parametrize()
def test_fibonacci():
    output = tackle('loop-condition.yaml', 'fibonacci', 8)

    assert output
